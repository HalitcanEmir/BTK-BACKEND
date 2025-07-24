from django.urls import path
from .views import login, register, verify_email, reset_password, my_profile, user_profile, edit_profile, edit_roles

urlpatterns = [
    path('register', register),
    path('login', login),
    path('verify-email', verify_email),
    path('reset-password', reset_password),
    path('me', my_profile),
    path('<str:id>', user_profile),
    path('me/edit', edit_profile),
    path('roles', edit_roles),
] 