from django.urls import path
from .views import (
    projects_list, project_detail, jobs_list, job_detail, project_team,
    approve_candidate, reject_candidate, project_plan, project_tasks,
    project_chat, project_ai_panel, completed_projects_list, list_active_projects,
    complete_project, request_project_completion, list_completion_requests,
    approve_completion_request, reject_completion_request, submit_investment_offer,
    approve_investment_offer, reject_investment_offer
)

urlpatterns = [
    # Önce completed_projects_list'i kontrol et
    path('', completed_projects_list),
    path('jobs', jobs_list),
    path('jobs/<str:id>', job_detail),
    # Yeni completion request endpoint'leri
    path('completion-requests', list_completion_requests),
    path('<str:id>/request-completion', request_project_completion),
    path('<str:project_id>/completion-requests/<str:request_id>/approve', approve_completion_request),
    path('<str:project_id>/completion-requests/<str:request_id>/reject', reject_completion_request),
    # Yatırım endpoint'leri
    path('<str:id>/invest', submit_investment_offer),
    path('<str:project_id>/investment-offers/<str:offer_id>/approve', approve_investment_offer),
    path('<str:project_id>/investment-offers/<str:offer_id>/reject', reject_investment_offer),
    # Daha spesifik URL'leri önce koy
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