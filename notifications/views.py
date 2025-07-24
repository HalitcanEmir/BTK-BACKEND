from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# Bildirim Merkezi
# GET /api/notifications/
# Açıklama: Kullanıcının bildirimlerini listeler
def notification_center(request):
    return JsonResponse({"message": "Bildirim Merkezi"})

# Hata Sayfası (404)
# GET /api/notifications/404
# Açıklama: Bulunamayan sayfa
def not_found(request):
    return JsonResponse({"message": "404 Not Found"})

# Yetkisiz Erişim Sayfası (403)
# GET /api/notifications/403
# Açıklama: Yetkisiz erişim
def forbidden(request):
    return JsonResponse({"message": "403 Forbidden"})

# Bakım Sayfası
# GET /api/notifications/maintenance
# Açıklama: Sistem bakımda
def maintenance(request):
    return JsonResponse({"message": "Bakım Sayfası"})
