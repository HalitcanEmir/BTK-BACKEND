from django.urls import path
from . import views
from .views import verify_id_view, upload_cv_view, my_profile, user_profile

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('me', views.my_profile, name='my_profile'),
    path('profile/', my_profile, name='my_profile'),
    path('profile/<str:user_id>/', user_profile, name='user_profile'),
    path('edit-roles', views.edit_roles, name='edit_roles'),
    path('verify-identity', views.verify_identity, name='verify_identity'),
    path('verify-id-card', views.verify_id_card, name='verify_id_card'),
    path('verify-linkedin', views.verify_linkedin, name='verify_linkedin'),
    path('verification-status', views.get_verification_status, name='verification_status'),
    path('admin/verification-requests', views.admin_verification_requests, name='admin_verification_requests'),
    path('admin/approve-verification', views.admin_approve_verification, name='admin_approve_verification'),
    path('admin/reject-verification', views.admin_reject_verification, name='admin_reject_verification'),
    # Email doğrulama endpoint'leri
    path('send-verification-code', views.send_verification_code, name='send_verification_code'),
    path('verify-email-and-register', views.verify_email_and_register, name='verify_email_and_register'),
    path('resend-verification-code', views.resend_verification_code, name='resend_verification_code'),
    path('test-email-settings', views.test_email_settings, name='test_email_settings'),
    # Şifre sıfırlama endpoint'leri
    path('send-password-reset-code', views.send_password_reset_code, name='send_password_reset_code'),
    path('verify-reset-code-and-change-password', views.verify_reset_code_and_change_password, name='verify_reset_code_and_change_password'),
    path('resend-password-reset-code', views.resend_password_reset_code, name='resend_password_reset_code'),
    # Profil yönetimi endpoint'leri
    path('update-profile', views.update_profile, name='update_profile'),
    path('upload-avatar', views.upload_avatar, name='upload_avatar'),
    path('delete-account', views.delete_account, name='delete_account'),
    # Arkadaşlık sistemi endpoint'leri
    path('send-friend-request', views.send_friend_request, name='send_friend_request'),
    path('respond-to-friend-request', views.respond_to_friend_request, name='respond_to_friend_request'),
    path('friend-requests', views.get_friend_requests, name='get_friend_requests'),
    path('friends', views.get_friends, name='get_friends'),
    path('remove-friend', views.remove_friend, name='remove_friend'),
]

urlpatterns += [
    path('verify-id/', verify_id_view, name='verify_id'),
    path('upload-cv/', upload_cv_view, name='upload_cv'),
] 