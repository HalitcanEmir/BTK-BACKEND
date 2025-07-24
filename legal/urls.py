from django.urls import path
from .views import terms, privacy, cookies

urlpatterns = [
    path('terms', terms),
    path('privacy', privacy),
    path('cookies', cookies),
] 