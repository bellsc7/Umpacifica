# users/serializers.py (ฉบับแก้ไขที่สมบูรณ์)

from rest_framework import serializers
from .models import User, Permission, System, Log

# ... SystemSerializer และ PermissionSerializer เหมือนเดิม ...
class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = ['id', 'name']

class PermissionSerializer(serializers.ModelSerializer):
    system = SystemSerializer(read_only=True)
    class Meta:
        model = Permission
        fields = ['id', 'name', 'system']

# --- แก้ไขคลาสนี้ให้มีฟิลด์ครบถ้วน ---
class UserSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Permission.objects.all(), source='permissions'
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name', 'email',
            'employee_id', 'full_name_eng', 'full_name_thai',
            'position', 'phone', 'company', 'department', 'brand', 'user_status',
            
            # --- เพิ่มฟิลด์ทั้งหมดที่ขาดไปกลับเข้ามา ---
            'has_pacifica_app',
            'has_color_printing',
            'has_cctv',
            'has_vpn',
            'has_wifi_other_devices',
            'software_request',
            'share_drive_request',
            
            'permissions',      # สำหรับ GET
            'permission_ids'    # สำหรับ POST/PUT
        ]
        # ทำให้ Password เป็นแบบ write-only (ไม่แสดงผลกลับไป)
        # --- แก้ไขส่วนนี้ ---
        extra_kwargs = {
            # บอกให้ password ไม่ใช่ field ที่ต้องกรอก แต่ยังคงรับค่าได้
            'password': {'write_only': True, 'required': False, 'allow_null': True}
        }

class LogSerializer(serializers.ModelSerializer):
    target_user_name = serializers.CharField(source='target_user.username', read_only=True)
    class Meta:
        model = Log
        fields = '__all__'