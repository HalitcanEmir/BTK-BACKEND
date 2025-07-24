from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# Ana Sayfa
# GET /api/core/home
# Açıklama: Platformun ana sayfası
# Response: {"message": "Ana Sayfa"}
def home(request):
    return JsonResponse({"message": "Ana Sayfa"})

# Hizmetimiz
# GET /api/core/service
# Açıklama: Platformun sunduğu hizmetler
# Response: {"message": "Hizmetimiz"}
def service(request):
    return JsonResponse({"message": "Hizmetimiz"})

# Hakkımızda
# GET /api/core/about
# Açıklama: Platform hakkında bilgiler
# Response: {"message": "Hakkımızda"}
def about(request):
    return JsonResponse({"message": "Hakkımızda"})

# İletişim
# GET /api/core/contact
# Açıklama: İletişim bilgileri
# Response: {"message": "İletişim"}
def contact(request):
    return JsonResponse({"message": "İletişim"})
