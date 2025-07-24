from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# Yatırımcı Ol Sayfası
# GET /api/investments/become
# Açıklama: Yatırımcı olma başvuru sayfası
def become_investor(request):
    return JsonResponse({"message": "Yatırımcı Ol Sayfası"})

# Proje Keşfet Sayfası
# GET /api/investments/explore
# Açıklama: Yatırım yapılabilir projeleri listeler
def explore_projects(request):
    return JsonResponse({"message": "Proje Keşfet Sayfası"})

# Takip Ettiğim Projeler
# GET /api/investments/following
# Açıklama: Kullanıcının takip ettiği projeler
def following_projects(request):
    return JsonResponse({"message": "Takip Ettiğim Projeler"})

# Yatırım Teklifi Gönderme Sayfası
# POST /api/investments/offer
# Açıklama: Yatırım teklifi gönderme işlemi
def send_offer(request):
    return JsonResponse({"message": "Yatırım Teklifi Gönderme Sayfası"})
