from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ideas.models import Idea
from users.models import User
import json
import jwt
from django.conf import settings
from datetime import datetime

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

# Yardımcı: JWT token'dan kullanıcıyı bul
def get_user_from_jwt(request):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return None
    token = auth.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get('email')
        return User.objects(email=email).first()
    except Exception:
        return None

@csrf_exempt
# Fikir gönderme endpointi
# POST /ideas
# Body: {"title": ..., "description": ..., ...}
# Response: {"status": "ok", "idea": {...}}
def submit_idea(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız (JWT gerekli)'}, status=401)
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        category = data.get('category')
        problem = data.get('problem')
        solution = data.get('solution')
        estimated_cost = data.get('estimated_cost')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    if not title:
        return JsonResponse({'status': 'error', 'message': 'Başlık zorunlu'})
    # Fikir kaydı
    idea = Idea(
        title=title,
        description=description,
        category=category,
        problem=problem,
        solution=solution,
        estimated_cost=estimated_cost,
        owner_id=user,
        status='pending',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    idea.save()
    # Kullanıcıya idea_owner rolü ekle (yoksa)
    if 'idea_owner' not in user.user_type:
        user.user_type.append('idea_owner')
        user.save()
    idea_data = {
        'id': str(idea.id),
        'title': idea.title,
        'status': idea.status,
        'owner_id': str(user.id),
        'created_at': str(idea.created_at)
    }
    return JsonResponse({'status': 'ok', 'idea': idea_data})
