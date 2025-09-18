# users/urls.py (ฉบับสมบูรณ์ที่แก้ไขใหม่ทั้งหมด)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PermissionViewSet, LogViewSet, SystemViewSet, get_csrf_token, LdapUserSearchView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'logs', LogViewSet, basename='log')
router.register(r'systems', SystemViewSet, basename='system')

urlpatterns = [
    path('ldap-search/<str:username>/', LdapUserSearchView.as_view(), name='ldap-search'),
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
    path('', include(router.urls)),
]