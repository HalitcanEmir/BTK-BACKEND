from django.urls import path
from .views import blog, faq, social, mentorship

urlpatterns = [
    path('blog', blog),
    path('faq', faq),
    path('social', social),
    path('mentorship', mentorship),
] 