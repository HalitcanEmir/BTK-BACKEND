from django.urls import path
from .views import ideas_list, idea_detail, idea_apply_page, idea_apply, submit_idea

urlpatterns = [
    path('', ideas_list),
    path('<str:id>', idea_detail),
    path('apply', idea_apply_page),
    path('apply/submit', idea_apply),
    path('submit-idea', submit_idea),  # POST /ideas/submit-idea
] 