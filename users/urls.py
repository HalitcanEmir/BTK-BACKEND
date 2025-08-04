from django.urls import path
from .views import login, register, verify_email, reset_password, my_profile, user_profile, edit_profile, edit_roles, reset_password_request, reset_password_confirm, verify_id_view, upload_cv_view, send_verification_code, verify_email_and_register, resend_verification_code, send_password_reset_code, verify_reset_code_and_change_password, resend_password_reset_code, update_profile, upload_avatar, delete_account, test_atlas_connection, list_users

urlpatterns = [
    path('register', register),
    path('login', login),
    path('verify-email', verify_email),
    path('reset-password', reset_password),
    path('me', my_profile),
    path('me/edit', edit_profile),
    path('roles', edit_roles),
    path('reset-password/', reset_password_request),  
    path('reset-password-confirm/<str:token>/', reset_password_confirm),
    # TC Kimlik Kartı ve CV Analizi Endpoint'leri
    path('verify-id-card', verify_id_view),
    path('upload-cv', upload_cv_view),
    # Email doğrulama endpoint'leri
    path('send-verification-code', send_verification_code),
    path('verify-email-and-register', verify_email_and_register),
    path('resend-verification-code', resend_verification_code),
    # Şifre sıfırlama endpoint'leri
    path('send-password-reset-code', send_password_reset_code),
    path('verify-reset-code-and-change-password', verify_reset_code_and_change_password),
    path('resend-password-reset-code', resend_password_reset_code),
    # Profil yönetimi endpoint'leri
    path('update-profile', update_profile),
    path('upload-avatar', upload_avatar),
    path('delete-account', delete_account),
    # Atlas bağlantı test endpoint'i
    path('test-atlas', test_atlas_connection),
    # Kullanıcı listesi endpoint'i
    path('list', list_users),
    # Kullanıcı profili - en sona taşındı çünkü genel pattern
    path('<str:user_id>', user_profile),
]
