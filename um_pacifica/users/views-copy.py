# users/views.py (ฉบับสมบูรณ์ที่ปรับปรุง Log)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from .models import User, Permission, Log, System
from .serializers import UserSerializer, PermissionSerializer, LogSerializer, SystemSerializer

# ----------------- ViewSet สำหรับการจัดการข้อมูล User -----------------
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Only accessible by Admin users.
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['get'], url_path='logs')
    def get_user_logs(self, request, pk=None):
        """
        Returns a list of all log entries for a specific user.
        """
        # ดึง User ที่ต้องการ
        user = self.get_object()
        # Query Log ที่มี target_user เป็น User คนนี้
        logs = Log.objects.filter(target_user=user).order_by('-timestamp')
        # ใช้ LogSerializer เพื่อแปลงข้อมูล
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)

    

    def _get_permission_names(self, permission_ids):
        """Helper function to get a sorted list of permission names from IDs."""
        if not permission_ids:
            return []
        # ดึงชื่อ Permission จาก ID ที่ได้รับมา
        permissions = Permission.objects.filter(id__in=permission_ids).select_related('system')
        return sorted([str(p) for p in permissions])

    def perform_create(self, serializer):
        """

        Custom logic for creating a new user.
        Logs detailed information about the creation, including granted permissions.
        """
        # บันทึก User ใหม่เพื่อรับ object กลับมา
        user = serializer.save()
        
        # ดึงชื่อของ permissions ที่ถูกเพิ่มเข้ามา
        # validated_data['permissions'] จะเป็น list of Permission objects
        added_permissions = self._get_permission_names(
            [p.id for p in serializer.validated_data.get('permissions', [])]
        )

        details = [f"User '{user.full_name_eng or user.username}' was created."]
        if added_permissions:
            details.append("\nPermissions Granted:")
            details.extend([f"- {name}" for name in added_permissions])

        Log.objects.create(
            # ผู้เปลี่ยนแปลงคือ User ที่ login อยู่
            actor=self.request.user.username,
            # Action บอกว่าเกิดอะไรขึ้น
            action=f"Created user: {user.username}",
            # User ที่ถูกกระทำ
            target_user=user,
            # รายละเอียดการเปลี่ยนแปลง
            details='\n'.join(details)
        )

    def perform_update(self, serializer):
        """
        Custom logic for updating an existing user.
        Logs detailed information about permission changes (granted and revoked).
        """
        # ดึงข้อมูล User เก่ามาก่อนที่จะบันทึก
        instance = self.get_object()
        old_permission_ids = set(instance.permissions.values_list('id', flat=True))

        # บันทึกข้อมูลใหม่
        user = serializer.save()

        # ดึงข้อมูล Permission ใหม่
        new_permission_ids = set(p.id for p in serializer.validated_data.get('permissions', []))
        
        # เปรียบเทียบเพื่อหา Permission ที่ถูกเพิ่มและลบ
        added_ids = new_permission_ids - old_permission_ids
        removed_ids = old_permission_ids - new_permission_ids

        added_permissions = self._get_permission_names(added_ids)
        removed_permissions = self._get_permission_names(removed_ids)

        # ถ้าไม่มีการเปลี่ยนแปลงใดๆ เกี่ยวกับ permission ก็ไม่ต้องบันทึก Log
        if not added_permissions and not removed_permissions:
            return # ออกจากฟังก์ชันไปเลย

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

# ----------------- ViewSets สำหรับให้ Frontend ดึงข้อมูลไปแสดง (Read-Only) -----------------
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that provides a list of all available permissions.
    """
    queryset = Permission.objects.select_related('system').all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated] # ให้ User ที่ login แล้วดูได้

class SystemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that provides a list of all available systems.
    """
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = [IsAuthenticated]

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that provides a list of all logs.
    Only accessible by Admin users.
    """
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAdminUser]

# ----------------- CSRF Token View -----------------
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    This view ensures that a CSRF cookie is always sent to the client.
    """
    return JsonResponse({"detail": "CSRF cookie set"})