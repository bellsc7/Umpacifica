# config/urls.py (ฉบับแก้ไข)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- ตรวจสอบว่ามี import นี้อยู่

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # --- เพิ่มบรรทัดนี้เข้าไป ---
    # เราจะเพิ่ม URL ของ debug_toolbar เข้าไปโดยตรง
    # และจะทำงานก็ต่อเมื่อ DEBUG=True เท่านั้น
    path('__debug__/', include('debug_toolbar.urls')),
]

# --- ลบโค้ดส่วน if settings.DEBUG ... ที่เราเคยเพิ่มไว้ท้ายไฟล์ทิ้งไปได้เลย ---