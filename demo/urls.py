from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_person, name='add_person'),
    path('list/', views.list_people, name='list_people'),
    path('test-mongodb/', views.test_mongodb_connection, name='test_mongodb'),
    path('request-login', views.request_login, name='request_login'),
    path('verify-login', views.verify_login, name='verify_login'),
] 