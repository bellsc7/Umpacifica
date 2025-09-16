# users/models.py (ฉบับสมบูรณ์ที่แก้ไขใหม่ทั้งหมด)

from django.db import models
from django.contrib.auth.models import AbstractUser

class System(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Permission(models.Model):
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='permissions')
    name = models.CharField(max_length=100)
    class Meta:
        ordering = ['system__name', 'name']
        unique_together = ('system', 'name')
    def __str__(self):
        return f'{self.system.name} - {self.name}'

class User(AbstractUser):
    # AbstractUser มี username, first_name, last_name, email, password, etc. มาให้แล้ว
    class UserStatus(models.TextChoices):
        NEW = 'New', 'New'
        CURRENT = 'Current', 'Current'
        EXTERNAL = 'External', 'External'

    # --- เพิ่มฟิลด์ทั้งหมดจาก from.html ---
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    full_name_eng = models.CharField(max_length=255, blank=True)
    full_name_thai = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    user_status = models.CharField(max_length=10, choices=UserStatus.choices, default=UserStatus.CURRENT)
    
    # --- เพิ่มฟิลด์สำหรับ Select System/Services ---
    # ใช้ ManyToManyField สำหรับ Permissions เหมือนเดิม
    permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_users')

    # ใช้ BooleanField สำหรับ Checkbox ทั่วไป
    has_pacifica_app = models.BooleanField(default=False)
    has_color_printing = models.BooleanField(default=False)
    has_cctv = models.BooleanField(default=False)
    has_vpn = models.BooleanField(default=False)
    has_wifi_other_devices = models.BooleanField(default=False)

    # ใช้ CharField สำหรับ Checkbox ที่มี Text input
    software_request = models.CharField(max_length=255, blank=True, help_text="เก็บชื่อ Software ที่ขอ")
    share_drive_request = models.CharField(max_length=255, blank=True, help_text="เก็บชื่อ Share Drive ที่ขอ")
    
    def __str__(self):
        return self.username

# --- โมเดล Request ถูกลบออกไป ---

class Log(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True)
    class Meta:
        ordering = ['-timestamp']
    def __str__(self):
        return f'{self.timestamp.strftime("%Y-%m-%d %H:%M")} - {self.action}'