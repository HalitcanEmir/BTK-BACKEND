from django.urls import path
from .views import ideas_list, idea_detail, idea_apply_page, idea_apply, submit_idea

urlpatterns = [
    path('submit-idea', submit_idea),  # Önce özel endpointler
    path('', ideas_list),
    path('apply', idea_apply_page),
    path('apply/submit', idea_apply),
    path('<str:id>', idea_detail),
] 