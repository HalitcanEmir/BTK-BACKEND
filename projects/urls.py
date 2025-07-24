from django.urls import path
from .views import (
    projects_list, project_detail, jobs_list, job_detail, project_team,
    approve_candidate, reject_candidate, project_plan, project_tasks,
    project_chat, project_ai_panel
)

urlpatterns = [
    path('', projects_list),
    path('<str:id>', project_detail),
    path('jobs', jobs_list),
    path('jobs/<str:id>', job_detail),
    path('<str:id>/team', project_team),
    path('<str:id>/team/approve', approve_candidate),
    path('<str:id>/team/reject', reject_candidate),
    path('<str:id>/plan', project_plan),
    path('<str:id>/tasks', project_tasks),
    path('<str:id>/chat', project_chat),
    path('<str:id>/ai', project_ai_panel),
] 