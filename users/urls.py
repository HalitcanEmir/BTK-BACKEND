from django.urls import path
from . import views
from .views import verify_id_view, upload_cv_view

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('me', views.my_profile, name='my_profile'),
    path('edit-roles', views.edit_roles, name='edit_roles'),
    path('verify-identity', views.verify_identity, name='verify_identity'),
    path('verify-id-card', views.verify_id_card, name='verify_id_card'),
    path('verify-linkedin', views.verify_linkedin, name='verify_linkedin'),
    path('verification-status', views.get_verification_status, name='verification_status'),
    path('admin/verification-requests', views.admin_verification_requests, name='admin_verification_requests'),
    path('admin/approve-verification', views.admin_approve_verification, name='admin_approve_verification'),
    path('admin/reject-verification', views.admin_reject_verification, name='admin_reject_verification'),
]

urlpatterns += [
    path('verify-id/', verify_id_view, name='verify_id'),
    path('upload-cv/', upload_cv_view, name='upload_cv'),
] 