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
        Logs detailed information about permission changes (granted and revoked).
        """
        instance = self.get_object()
        old_permission_ids = set(instance.permissions.values_list('id', flat=True))
        user = serializer.save()
        new_permission_ids = set(p.id for p in serializer.validated_data.get('permissions', []))
        added_ids = new_permission_ids - old_permission_ids
        removed_ids = old_permission_ids - new_permission_ids
        added_permissions = self._get_permission_names(added_ids)
        removed_permissions = self._get_permission_names(removed_ids)
        if not added_permissions and not removed_permissions:
            return
        details = [f"Permissions updated for user '{user.full_name_eng or user.username}'."]
        if added_permissions:
            details.append("\nPermissions Granted:")
            details.extend([f"- {name}" for name in added_permissions])
        if removed_permissions:
            details.append("\nPermissions Revoked:")
            details.extend([f"- {name}" for name in removed_permissions])
        Log.objects.create(
            actor=self.request.user.username,
            action=f"Updated permissions for user: {user.username}",
            target_user=user,
            details='\n'.join(details)
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


