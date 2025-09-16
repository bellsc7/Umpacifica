# users/views.py (ฉบับสมบูรณ์ที่แก้ไขใหม่ทั้งหมด)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser # ใช้ Permission ของ Admin
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from .models import User, Permission, Log, System
from .serializers import UserSerializer, PermissionSerializer, LogSerializer, SystemSerializer

# --- สร้าง UserViewSet สำหรับการจัดการข้อมูล User โดยตรง ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('first_name')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # อนุญาตให้เฉพาะ Admin ใช้งาน

    def perform_create(self, serializer):
        user = serializer.save()
        Log.objects.create(
            actor=self.request.user.username,
            action=f"Created new user: {user.username}",
            target_user=user,
            details=f"User '{user.full_name_eng}' was created."
        )

    def perform_update(self, serializer):
        user = serializer.save()
        Log.objects.create(
            actor=self.request.user.username,
            action=f"Updated user: {user.username}",
            target_user=user,
            details=f"User profile for '{user.full_name_eng}' was updated."
        )

# --- ViewSet สำหรับให้ Frontend ดึงข้อมูลไปแสดง ---
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.select_related('system').all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]

class SystemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = [IsAdminUser]

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAdminUser]

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"detail": "CSRF cookie set"})