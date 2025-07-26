from django.urls import path
from . import views

urlpatterns = [
    path('', views.ideas_list, name='ideas_list'),
    path('submit-idea', views.submit_idea, name='submit_idea'),
    path('<str:id>', views.idea_detail, name='idea_detail'),
    path('<str:id>/swipe', views.swipe_vote, name='swipe_vote'),
    path('<str:idea_id>/join-request', views.join_request, name='join_request'),
    path('<str:idea_id>/join-requests/me', views.join_request_status, name='join_request_status'),
    path('admin/ideas', views.admin_list_pending_ideas, name='admin_list_pending_ideas'),
    path('admin/ideas/<str:id>/approve', views.admin_approve_idea, name='admin_approve_idea'),
    path('admin/ideas/<str:id>/reject', views.admin_reject_idea, name='admin_reject_idea'),
    path('admin/join-requests', views.admin_list_join_requests, name='admin_list_join_requests'),
    path('admin/join-requests/<str:id>/approve', views.admin_approve_join_request, name='admin_approve_join_request'),
    path('admin/join-requests/<str:id>/reject', views.admin_reject_join_request, name='admin_reject_join_request'),
    path('<str:idea_id>/chat', views.idea_project_chat, name='idea_project_chat'),
    path('analyze-project/', views.analyze_project_view, name='analyze_project'),
    path('save-analysis/', views.save_project_analysis_view, name='save_project_analysis'),
] 