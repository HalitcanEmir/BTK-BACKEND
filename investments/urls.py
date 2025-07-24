from django.urls import path
from .views import become_investor, explore_projects, following_projects, send_offer

urlpatterns = [
    path('become', become_investor),
    path('explore', explore_projects),
    path('following', following_projects),
    path('offer', send_offer),
] 