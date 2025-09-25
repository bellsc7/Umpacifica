# users/serializers.py (ฉบับสมบูรณ์)

from rest_framework import serializers
from .models import User, Permission, System, Log

class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = ['id', 'name']

class PermissionSerializer(serializers.ModelSerializer):
    system = SystemSerializer(read_only=True)
    class Meta:
        model = Permission
        fields = ['id', 'name', 'system']

class LogSerializer(serializers.ModelSerializer):
    target_user_name = serializers.CharField(source='target_user.username', read_only=True, default='')
    class Meta:
        model = Log
        fields = '__all__'

# --- Serializer สำหรับ "อ่าน" ข้อมูล (Read-Only) ---
class UserSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser',
            'employee_id', 'full_name_eng', 'full_name_thai', 'position',
            'phone', 'company', 'department', 'brand', 'user_status',
            'has_pacifica_app', 'has_color_printing', 'has_cctv',
            'has_vpn', 'has_wifi_other_devices',
            'software_request', 'share_drive_request',
            'permissions',
        ]

# --- Serializer สำหรับ "เขียน" ข้อมูล (Create/Update) ---
class UserWriteSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), source='permissions', required=False
    )
    class Meta:
        model = User
        fields = [
            'username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser',
            'employee_id', 'full_name_eng', 'full_name_thai', 'position',
            'phone', 'company', 'department', 'brand', 'user_status',
            'has_pacifica_app', 'has_color_printing', 'has_cctv',
            'has_vpn', 'has_wifi_other_devices',
            'software_request', 'share_drive_request',
            'permission_ids',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'allow_null': True}
        }