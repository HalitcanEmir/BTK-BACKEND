from django.urls import path
from .views import notification_center, not_found, forbidden, maintenance

urlpatterns = [
    path('', notification_center),
    path('404', not_found),
    path('403', forbidden),
    path('maintenance', maintenance),
] 