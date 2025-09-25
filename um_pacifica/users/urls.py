# users/urls.py (ฉบับเต็ม)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, PermissionViewSet, LogViewSet, SystemViewSet, get_csrf_token,
    LdapUserSearchView, LoginView, LogoutView, CurrentUserView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'logs', LogViewSet, basename='log')
router.register(r'systems', SystemViewSet, basename='system')

urlpatterns = [
    # --- ตรวจสอบว่ามี 3 บรรทัดนี้อยู่ ---
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
    path('me/', CurrentUserView.as_view(), name='current-user'),

    # ... URL อื่นๆ เหมือนเดิม ...
    path('ldap-search/<str:username>/', LdapUserSearchView.as_view(), name='ldap-search'),
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
    path('', include(router.urls)),
]