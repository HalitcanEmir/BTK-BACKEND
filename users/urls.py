from django.urls import path
from .views import login, register, verify_email, reset_password, my_profile, user_profile, edit_profile, edit_roles

urlpatterns = [
    path('auth/login', login),
    path('auth/register', register),
    path('auth/verify-email', verify_email),
    path('auth/reset-password', reset_password),
    path('users/me', my_profile),
    path('users/<str:id>', user_profile),
    path('users/me/edit', edit_profile),
    path('users/roles', edit_roles),
] 