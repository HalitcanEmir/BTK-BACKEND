from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# Kullanım Şartları
# GET /api/legal/terms
# Açıklama: Platformun kullanım şartları
# Response: {"message": "Kullanım Şartları"}
def terms(request):
    return JsonResponse({"message": "Kullanım Şartları"})

# Gizlilik Politikası
# GET /api/legal/privacy
# Açıklama: Gizlilik politikası
# Response: {"message": "Gizlilik Politikası"}
def privacy(request):
    return JsonResponse({"message": "Gizlilik Politikası"})

# Çerez Politikası
# GET /api/legal/cookies
# Açıklama: Çerez politikası
# Response: {"message": "Çerez Politikası"}
def cookies(request):
    return JsonResponse({"message": "Çerez Politikası"})
