from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# Fikirler Sayfası
# GET /api/ideas/
# Açıklama: Tüm fikirleri listeler
def ideas_list(request):
    return JsonResponse({"message": "Fikirler Sayfası"})

# Fikir Detay Sayfası
# GET /api/ideas/<id>
# Açıklama: Belirli bir fikrin detayını getirir
def idea_detail(request, id):
    return JsonResponse({"message": f"Fikir Detay Sayfası: {id}"})

# Fikir Başvurma Sayfası
# GET /api/ideas/apply
# Açıklama: Fikre başvuru formu sayfası
def idea_apply_page(request):
    return JsonResponse({"message": "Fikir Başvurma Sayfası"})

# Fikre Başvuru Formu
# POST /api/ideas/apply
# Açıklama: Fikre başvuru işlemi
def idea_apply(request):
    return JsonResponse({"message": "Fikre Başvuru Formu"})
