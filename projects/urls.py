from django.urls import path
from .views import (
    projects_list, project_detail, jobs_list, job_detail, project_team,
    approve_candidate, reject_candidate, project_plan, project_tasks,
    project_chat, project_ai_panel, completed_projects_list, list_active_projects,
    complete_project, request_project_completion, list_completion_requests,
    approve_completion_request, reject_completion_request, submit_investment_offer,
    approve_investment_offer, reject_investment_offer, leaderboard, toggle_project_like,
    analyze_project_ai, get_project_investment_advice, get_user_project_suggestions,
    project_join_request, project_join_request_status, admin_list_project_join_requests,
    admin_approve_project_join_request, admin_reject_project_join_request
)

urlpatterns = [
    # Liderlik sayfası
    path('leaderboard', leaderboard),
    # Önce completed_projects_list'i kontrol et
    path('', completed_projects_list),
    path('jobs', jobs_list),
    path('jobs/<str:id>', job_detail),
    # Yeni completion request endpoint'leri
    path('completion-requests', list_completion_requests),
    path('users/suggestions', get_user_project_suggestions),
    # Daha spesifik URL'leri önce koy
    path('<str:id>/request-completion', request_project_completion),
    path('<str:project_id>/completion-requests/<str:request_id>/approve', approve_completion_request),
    path('<str:project_id>/completion-requests/<str:request_id>/reject', reject_completion_request),
    # Yatırım endpoint'leri
    path('<str:id>/invest', submit_investment_offer),
    path('<str:project_id>/investment-offers/<str:offer_id>/approve', approve_investment_offer),
    path('<str:project_id>/investment-offers/<str:offer_id>/reject', reject_investment_offer),
    # AI endpoint'leri
    path('<str:id>/analyze', analyze_project_ai),
    path('<str:id>/investment-advice', get_project_investment_advice),
    # Beğeni endpoint'i
    path('<str:id>/like', toggle_project_like),
    # Proje başvuru endpoint'leri
    path('<str:id>/join-request', project_join_request),
    path('<str:id>/join-request/status', project_join_request_status),
    # Admin proje başvuru endpoint'leri
    path('admin/join-requests', admin_list_project_join_requests),
    path('admin/join-requests/<str:request_id>/approve', admin_approve_project_join_request),
    path('admin/join-requests/<str:request_id>/reject', admin_reject_project_join_request),
    # Diğer spesifik endpoint'ler
    path('<str:id>/complete', complete_project),
    path('<str:id>/team', project_team),
    path('<str:id>/team/approve', approve_candidate),
    path('<str:id>/team/reject', reject_candidate),
    path('<str:id>/plan', project_plan),
    path('<str:id>/tasks', project_tasks),
    path('<str:id>/chat', project_chat),
    path('<str:id>/ai', project_ai_panel),
    # En genel URL'yi en sona koy
    path('<str:id>', project_detail),
] 