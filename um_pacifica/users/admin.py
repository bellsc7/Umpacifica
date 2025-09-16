# users/admin.py (ฉบับสมบูรณ์ที่แก้ไขใหม่ทั้งหมด)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, System, Permission, Log

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name_eng', 'department', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Application Profile', {
            'fields': (
                'employee_id', 'full_name_eng', 'full_name_thai', 'position',
                'phone', 'company', 'department', 'brand', 'user_status'
            )
        }),
         ('System / Services Access', {
            'fields': (
                'has_pacifica_app', 'has_color_printing', 'has_cctv',
                'has_vpn', 'has_wifi_other_devices',
                'software_request', 'share_drive_request'
            )
        }),
        
        ('Application Permissions', {
            'fields': ('permissions',)
        }),
    )
    filter_horizontal = ('permissions',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(System)
admin.site.register(Permission)
admin.site.register(Log)