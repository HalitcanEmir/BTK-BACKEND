from django.urls import path
from .views import ideas_list, idea_detail, idea_apply_page, idea_apply

urlpatterns = [
    path('', ideas_list),
    path('<str:id>', idea_detail),
    path('apply', idea_apply_page),
    path('apply/submit', idea_apply),
] 