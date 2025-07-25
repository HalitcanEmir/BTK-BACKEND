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
# GET /ideas
# Açıklama: Onaylanmış fikirleri listeler, filtreleme, arama, sıralama ve pagination destekler
@csrf_exempt
def ideas_list(request):
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız (JWT gerekli)'}, status=401)
    # Query parametreleri
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    q = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort', 'created_at')

    # Sadece onaylanmış fikirler
    ideas = Idea.objects(status="approved")

    # Arama filtresi
    if q:
        ideas = ideas.filter(__raw__={
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}}
            ]
        })
    # Kategori filtresi
    if category:
        ideas = ideas.filter(category=category)

    # Sıralama
    if sort == "likes":
        # likes alanı modelde yok, 0 olarak dönecek
        pass
    elif sort == "swipe_score":
        # swipe_score alanı modelde yok, 0.0 olarak dönecek
        pass
    else:
        ideas = ideas.order_by("-created_at")

    total = ideas.count()
    ideas = ideas.skip((page - 1) * limit).limit(limit)

    data = []
    for idea in ideas:
        created_by_user = idea.created_by
        data.append({
            'id': str(idea.id),
            'title': idea.title,
            'description': idea.description,
            'category': idea.category,
            'created_by': {
                'id': str(created_by_user.id) if created_by_user else None,
                'name': created_by_user.full_name if created_by_user else None
            },
            'created_at': idea.created_at.isoformat() if idea.created_at else None,
            'likes': 0,  # Like sistemi eklenince güncellenecek
            'swipe_score': 0.0  # Swipe sistemi eklenince güncellenecek
        })
    return JsonResponse({
        'total': total,
        'page': page,
        'limit': limit,
        'ideas': data
    })

# Fikir Detay Sayfası
# GET /ideas/<id>
# Açıklama: Belirli bir fikrin detayını getirir
@csrf_exempt
def idea_detail(request, id):
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız (JWT gerekli)'}, status=401)
    idea = Idea.objects(id=id, status="approved").first()
    if not idea:
        return JsonResponse({'status': 'error', 'message': 'Fikir bulunamadı veya onaylanmamış'}, status=404)
    created_by_user = idea.created_by
    approved_by_user = idea.approved_by
    data = {
        'id': str(idea.id),
        'title': idea.title,
        'description': idea.description,
        'created_by': {
            'id': str(created_by_user.id) if created_by_user else None,
            'name': created_by_user.full_name if created_by_user else None
        },
        'created_at': idea.created_at.isoformat() if idea.created_at else None,
        'approved_by': {
            'id': str(approved_by_user.id) if approved_by_user else None,
            'name': approved_by_user.full_name if approved_by_user else None
        } if approved_by_user else None,
        'approved_at': idea.approved_at.isoformat() if idea.approved_at else None,
        'license': {
            'accepted': idea.license_accepted,
            'accepted_at': idea.license_accepted_at.isoformat() if idea.license_accepted_at else None,
            'owner_share_percent': idea.owner_share_percent
        },
        'likes': 0,  # Like sistemi eklenince güncellenecek
        'swipe_score': 0.0  # Swipe sistemi eklenince güncellenecek
    }
    return JsonResponse(data)

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

def is_admin(user):
    return user and ('admin' in getattr(user, 'user_type', []) or 'admin' in getattr(user, 'roles', []))

from bson import ObjectId

@csrf_exempt
# GET /admin/ideas?status=pending
# Sadece admin erişebilir, bekleyen fikirleri listeler
def admin_list_pending_ideas(request):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    status_param = request.GET.get('status', 'pending_admin_approval')
    ideas = Idea.objects(status=status_param)
    data = [{
        'id': str(idea.id),
        'title': idea.title,
        'description': idea.description,
        'status': idea.status,
        'created_by': str(idea.created_by.id) if idea.created_by else None,
        'created_at': str(idea.created_at)
    } for idea in ideas]
    return JsonResponse({'status': 'ok', 'ideas': data})

@csrf_exempt
# PATCH /admin/ideas/<id>/approve
# Sadece admin erişebilir, fikri onaylar
def admin_approve_idea(request, id):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    try:
        idea = Idea.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz ID'}, status=400)
    if not idea or idea.status != 'pending_admin_approval':
        return JsonResponse({'status': 'error', 'message': 'Onay bekleyen fikir bulunamadı'}, status=404)
    now = datetime.utcnow()
    idea.status = 'approved'
    idea.approved_at = now
    idea.approved_by = user
    idea.save()
    return JsonResponse({'status': 'ok', 'message': 'Fikir onaylandı'})

@csrf_exempt
# PATCH /admin/ideas/<id>/reject
# Sadece admin erişebilir, fikri reddeder
def admin_reject_idea(request, id):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    try:
        idea = Idea.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz ID'}, status=400)
    if not idea or idea.status != 'pending_admin_approval':
        return JsonResponse({'status': 'error', 'message': 'Onay bekleyen fikir bulunamadı'}, status=404)
    try:
        data = json.loads(request.body)
        reason = data.get('reason')
    except Exception:
        reason = None
    now = datetime.utcnow()
    idea.status = 'rejected'
    idea.rejected_at = now
    idea.rejected_by = user
    idea.rejection_reason = reason
    idea.save()
    return JsonResponse({'status': 'ok', 'message': 'Fikir reddedildi'})

@csrf_exempt
# Fikir gönderme endpointi
# POST /ideas
# Body: {"title": ..., "description": ..., "license_accepted": true, ...}
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
        license_accepted = data.get('license_accepted')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    if not title:
        return JsonResponse({'status': 'error', 'message': 'Başlık zorunlu'})
    if not license_accepted:
        return JsonResponse({'status': 'error', 'message': 'Fikrin kaydedilebilmesi için lisans sözleşmesi kabul edilmelidir.'}, status=400)
    now = datetime.utcnow()
    # Fikir kaydı
    idea = Idea(
        title=title,
        description=description,
        category=category,
        problem=problem,
        solution=solution,
        estimated_cost=estimated_cost,
        owner_id=user,
        created_by=user,
        license_accepted=True,
        license_accepted_at=now,
        owner_share_percent=10,
        status='pending_admin_approval',
        created_at=now,
        updated_at=now
    )
    idea.save()
    # Kullanıcıya fikir_sahibi rolü ekle (yoksa)
    if 'fikir_sahibi' not in user.user_type:
        user.user_type.append('fikir_sahibi')
        user.save()
    idea_data = {
        'id': str(idea.id),
        'title': idea.title,
        'status': idea.status,
        'owner_id': str(user.id),
        'license_accepted': idea.license_accepted,
        'license_accepted_at': str(idea.license_accepted_at),
        'owner_share_percent': idea.owner_share_percent,
        'created_at': str(idea.created_at)
    }
    return JsonResponse({'status': 'ok', 'idea': idea_data})
