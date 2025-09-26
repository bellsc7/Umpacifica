# users/views.py (ฉบับเต็มที่เพิ่ม Action สำหรับดึง Log)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action # ตรวจสอบว่ามี import นี้
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login as django_login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import User, Permission, Log, System
from .serializers import (
    UserSerializer, UserWriteSerializer, PermissionSerializer, 
    LogSerializer, SystemSerializer
)
import ldap
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.conf import settings

# ----------------- ViewSet สำหรับการจัดการข้อมูล User -----------------
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Only accessible by Admin users.
    """
    queryset = User.objects.all().order_by('username')
    #serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
     # --- เพิ่ม Action นี้เข้าไป ---
    @action(detail=True, methods=['post'], url_path='revoke')

    def revoke_user(self, request, pk=None):
        """
        Action to revoke a user's access.
        Sets the user's is_active flag to False.
        """
        try:
            user_to_revoke = self.get_object()
            
            # ตรวจสอบว่า User ยังไม่ถูก Revoke ไปแล้ว
            if not user_to_revoke.is_active:
                return Response(
                    {'error': 'User is already revoked.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --- Logic การ Revoke ---
            user_to_revoke.is_active = False
            user_to_revoke.save()
            
            # --- บันทึก Log ---
            Log.objects.create(
                actor=request.user.username,
                action=f"Revoked user access: {user_to_revoke.username}",
                target_user=user_to_revoke,
                details=f"User '{user_to_revoke.full_name_eng or user_to_revoke.username}' has been revoked."
            )

            return Response({'status': f'User {user_to_revoke.username} has been successfully revoked.'})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_serializer_class(self):
        """
        Return the serializer class to use for the request.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return UserWriteSerializer
        return UserSerializer # Default for list, retrieve

    def perform_create(self, serializer):
        """
        Custom logic for creating a new user.
        Sets a dummy, unusable password.
        """
        # --- แก้ไขส่วนนี้: ตั้งค่า Password ที่ใช้งานไม่ได้ ---
        user = serializer.save()
        user.set_unusable_password()
        user.save()


    def _get_permission_names(self, permission_ids):
        """Helper function to get a sorted list of permission names from IDs."""
        if not permission_ids:
            return []
        permissions = Permission.objects.filter(id__in=permission_ids).select_related('system')
        return sorted([str(p) for p in permissions])

    def perform_create(self, serializer):
        """
        Custom logic for creating a new user.
        Logs detailed information about the creation, including granted permissions.
        """
        user = serializer.save()
        added_permissions = self._get_permission_names(
            [p.id for p in serializer.validated_data.get('permissions', [])]
        )
        details = [f"User '{user.full_name_eng or user.username}' was created."]
        if added_permissions:
            details.append("\nPermissions Granted:")
            details.extend([f"- {name}" for name in added_permissions])
        Log.objects.create(
            actor=self.request.user.username,
            action=f"Created user: {user.username}",
            target_user=user,
            details='\n'.join(details)
        )

    def perform_update(self, serializer):
        """
        Custom logic for updating an existing user.
        Logs detailed information about ALL changes, including profile fields,
        system services, and permission levels.
        """
        # 1. ดึงข้อมูลเก่า (instance) มาเก็บไว้ก่อน
        instance = self.get_object()
        
        # สร้าง Dictionary เพื่อเก็บค่าเก่าของฟิลด์ที่เราสนใจ
        old_data = {
            # Profile fields (ตัวอย่าง)
            'full_name_eng': instance.full_name_eng,
            'department': instance.department,
            # System/Services fields
            'has_pacifica_app': instance.has_pacifica_app,
            'has_color_printing': instance.has_color_printing,
            'has_cctv': instance.has_cctv,
            'has_vpn': instance.has_vpn,
            'has_wifi_other_devices': instance.has_wifi_other_devices,
            'software_request': instance.software_request,
            'share_drive_request': instance.share_drive_request,
            # Permission Level (เก็บเป็น Set ของ ID)
            'permissions': set(instance.permissions.values_list('id', flat=True))
        }

        # 2. บันทึกข้อมูลใหม่
        updated_user = serializer.save()

        # 3. สร้าง List เพื่อเก็บข้อความการเปลี่ยนแปลง
        change_details = []

        # 4. เปรียบเทียบฟิลด์ธรรมดา (Profile & Text Services)
        #    สร้าง "pretty names" เพื่อให้ Log อ่านง่าย
        fields_to_check = {
            'full_name_eng': 'Full Name (Eng)',
            'department': 'Department',
            'software_request': 'Software Request',
            'share_drive_request': 'Share Drive Request',
        }
        for field, pretty_name in fields_to_check.items():
            old_value = old_data[field]
            new_value = getattr(updated_user, field)
            if old_value != new_value:
                change_details.append(f"- {pretty_name}: changed from '{old_value}' to '{new_value}'")

        # 5. เปรียบเทียบ Checkbox (System/Services)
        checkbox_fields_to_check = {
            'has_pacifica_app': 'Pacifica App',
            'has_color_printing': 'Color Printing',
            'has_cctv': 'CCTV',
            'has_vpn': 'VPN',
            'has_wifi_other_devices': 'Wifi for other devices',
        }
        for field, pretty_name in checkbox_fields_to_check.items():
            old_value = old_data[field]
            new_value = getattr(updated_user, field)
            if old_value != new_value:
                status = "Granted" if new_value else "Revoked"
                change_details.append(f"- Service '{pretty_name}': {status}")

        # 6. เปรียบเทียบ Permission Level (เหมือนเดิม แต่ปรับปรุงเล็กน้อย)
        new_permission_ids = set(p.id for p in serializer.validated_data.get('permissions', []))
        added_ids = new_permission_ids - old_data['permissions']
        removed_ids = old_data['permissions'] - new_permission_ids

        if added_ids:
            added_permissions = self._get_permission_names(added_ids)
            change_details.append("\nPermissions Granted:")
            change_details.extend([f"  - {name}" for name in added_permissions])
        
        if removed_ids:
            removed_permissions = self._get_permission_names(removed_ids)
            change_details.append("\nPermissions Revoked:")
            change_details.extend([f"  - {name}" for name in removed_permissions])
            
        # 7. ถ้ามีการเปลี่ยนแปลงเกิดขึ้น ให้บันทึก Log
        if change_details:
            # สร้างข้อความ Header
            log_header = f"User profile for '{updated_user.full_name_eng or updated_user.username}' was updated."
            # รวม Header เข้ากับรายละเอียดการเปลี่ยนแปลง
            final_details = [log_header] + change_details
            
            Log.objects.create(
                actor=self.request.user.username,
                action=f"Updated user: {updated_user.username}",
                target_user=updated_user,
                details='\n'.join(final_details)
            )

    # --- เพิ่ม Action นี้เข้าไป ---
    @action(detail=True, methods=['get'], url_path='logs')
    def get_user_logs(self, request, pk=None):
        """
        Returns a list of all log entries for a specific user.
        """
        user = self.get_object()
        logs = Log.objects.filter(target_user=user).order_by('-timestamp')
        # ใช้ LogSerializer ที่มี `fields = '__all__'` เพื่อให้ได้ข้อมูลครบ
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)

# ----------------- ViewSets สำหรับให้ Frontend ดึงข้อมูลไปแสดง (Read-Only) -----------------
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.select_related('system').all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

class SystemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = [IsAuthenticated]

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAdminUser]

class LdapUserSearchView(APIView):
    """
    API endpoint to search for a user in LDAP and return their attributes
    WITHOUT creating or modifying any local Django user.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, username):
        if User.objects.filter(username__iexact=username).exists():
            return Response(
                {"error": f"User '{username}' already exists in this application."},
                status=status.HTTP_409_CONFLICT
            )
        try:
            con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            con.protocol_version = ldap.VERSION3
            con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

            search_base = settings.AUTH_LDAP_USER_SEARCH.base_dn
            search_filter = settings.AUTH_LDAP_USER_SEARCH.filterstr % {'user': username}
            required_attrs = list(settings.AUTH_LDAP_USER_ATTR_MAP.values())
            
            result = con.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter, required_attrs)

            if not result:
                return Response({"error": "User not found in LDAP"}, status=status.HTTP_404_NOT_FOUND)

            user_dn, ldap_data = result[0]
             # ---!!! เพิ่ม PRINT STATEMENT ตรงนี้ !!!---
            print("--- LDAP Data Received ---")
            print(ldap_data)
            print("--------------------------")
            user_data_to_return = {}
            
            for django_field, ldap_attr in settings.AUTH_LDAP_USER_ATTR_MAP.items():
                if ldap_attr in ldap_data:
                    user_data_to_return[django_field] = ldap_data[ldap_attr][0].decode('utf-8')

            return Response(user_data_to_return)

        except ldap.LDAPError as e:
            return Response({"error": f"LDAP Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if 'con' in locals() and con:
                con.unbind_s()

class LoginView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        print("\n--- [DEBUG] LOGIN ATTEMPT ---")
        print(f"Attempting login for user: {username}")

        if not username or not password:
            print("[DEBUG] FAILED: Username or password not provided.")
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            print(f"[DEBUG] SUCCESS: authenticate() returned user object: {user.username}")
            print(f"[DEBUG] User is staff: {user.is_staff}")
            print(f"[DEBUG] User is superuser: {user.is_superuser}")
            
            django_login(request, user)
            print("[DEBUG] django_login() called successfully. Session should be created.")
            
            token, created = Token.objects.get_or_create(user=user)
            print(f"[DEBUG] Token created/retrieved: {token.key}")
            print("--- [DEBUG] LOGIN END ---\n")
            return Response({'token': token.key})
        else:
            print("[DEBUG] FAILED: authenticate() returned None.")
            print("--- [DEBUG] LOGIN END ---\n")
            return Response({'error': 'Unable to log in with provided credentials.'}, status=status.HTTP_400_BAD_REQUEST)
            
class LogoutView(APIView):
    """API endpoint for user logout, deletes auth token."""
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        # ลบ Token ของผู้ใช้ที่ส่ง request มา
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CurrentUserView(APIView):
    """
    API endpoint to get information about the currently logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user ตอนนี้คือ Custom User Model ของเราโดยตรง
        # เราจึงสามารถส่งมันเข้าไปใน Serializer ได้เลย
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
# ----------------- CSRF Token View -----------------
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"detail": "CSRF cookie set"})


