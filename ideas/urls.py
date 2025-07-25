from django.urls import path
from .views import ideas_list, idea_detail, idea_apply_page, idea_apply, submit_idea, admin_list_pending_ideas, admin_approve_idea, admin_reject_idea, swipe_vote, join_request, join_request_status, admin_list_join_requests, admin_approve_join_request, admin_reject_join_request

urlpatterns = [
    path('submit-idea', submit_idea),
    path('admin/ideas', admin_list_pending_ideas),  # GET /ideas/admin/ideas?status=pending
    path('admin/ideas/<str:id>/approve', admin_approve_idea),  # PATCH /ideas/admin/ideas/:id/approve
    path('admin/ideas/<str:id>/reject', admin_reject_idea),    # PATCH /ideas/admin/ideas/:id/reject
    path('', ideas_list),
    path('apply', idea_apply_page),
    path('apply/submit', idea_apply),
    path('<str:id>', idea_detail),
    path('<str:id>/swipe', swipe_vote),
    path('<str:idea_id>/join-request', join_request),
    path('<str:idea_id>/join-requests/me', join_request_status),
]

urlpatterns += [
    path('admin/project-join-requests', admin_list_join_requests),
    path('admin/project-join-requests/<str:id>/approve', admin_approve_join_request),
    path('admin/project-join-requests/<str:id>/reject', admin_reject_join_request),
] 