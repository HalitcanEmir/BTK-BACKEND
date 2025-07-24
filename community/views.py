from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# Blog / Duyurular
# GET /api/community/blog
# Açıklama: Blog yazıları ve duyurular
def blog(request):
    return JsonResponse({"message": "Blog / Duyurular"})

# SSS
# GET /api/community/faq
# Açıklama: Sıkça sorulan sorular
def faq(request):
    return JsonResponse({"message": "SSS"})

# Topluluk Sayfası
# GET /api/community/social
# Açıklama: Youtube, etkinlik bağlantıları
def social(request):
    return JsonResponse({"message": "Topluluk Sayfası"})

# Mentorluk Başvuru Sayfası
# GET /api/community/mentorship
# Açıklama: Mentorluk başvuru formu
def mentorship(request):
    return JsonResponse({"message": "Mentorluk Başvuru Sayfası"})
