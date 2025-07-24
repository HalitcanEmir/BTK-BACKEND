from django.urls import path
from .views import home, service, about, contact

urlpatterns = [
    path('home', home),
    path('service', service),
    path('about', about),
    path('contact', contact),
] 