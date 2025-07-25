from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ideas.models import Idea
from users.models import User
import json
import jwt
from django.conf import settings
from datetime import datetime
from .models import SwipeVote
from .models import JoinRequest

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

@csrf_exempt
def swipe_vote(request, id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    try:
        data = json.loads(request.body)
        vote = data.get("vote")
        if vote not in ["like", "dislike", "pass"]:
            return JsonResponse({"status": "error", "message": "Geçersiz oy türü"}, status=400)
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)

    idea = Idea.objects(id=id, status="approved").first()
    if not idea:
        return JsonResponse({"status": "error", "message": "Fikir bulunamadı"}, status=404)

    # Aynı kullanıcı aynı fikre daha önce oy verdi mi?
    existing = SwipeVote.objects(idea=idea, user=user).first()
    if existing:
        return JsonResponse({"status": "error", "message": "Bu fikre zaten oy verdiniz."}, status=400)

    # Oy kaydı oluştur
    SwipeVote(idea=idea, user=user, vote=vote).save()

    # Fikirde oy sayılarını güncelle
    if vote == "like":
        idea.likes = (idea.likes or 0) + 1
    elif vote == "dislike":
        idea.dislikes = (idea.dislikes or 0) + 1
    elif vote == "pass":
        idea.passes = (idea.passes or 0) + 1

    # Swipe score güncelle (örnek: like=+1, dislike=-1, pass=+0.5)
    total_votes = (idea.likes or 0) + (idea.dislikes or 0) + (idea.passes or 0)
    if total_votes > 0:
        idea.swipe_score = ((idea.likes or 0) * 1 + (idea.dislikes or 0) * -1 + (idea.passes or 0) * 0.5) / total_votes
    idea.save()

    return JsonResponse({"status": "ok", "message": "Oyunuz kaydedildi."})

@csrf_exempt
def join_request(request, idea_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    try:
        data = json.loads(request.body)
        note = data.get("note", "")
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)

    idea = Idea.objects(id=idea_id, status="approved").first()
    if not idea:
        return JsonResponse({"status": "error", "message": "Fikir bulunamadı"}, status=404)

    existing = JoinRequest.objects(idea=idea, user=user).first()
    if existing:
        return JsonResponse({"status": "error", "message": "Zaten başvurdunuz."}, status=400)

    JoinRequest(idea=idea, user=user, note=note).save()
    return JsonResponse({"status": "ok", "message": "Başvurunuz alındı."})

@csrf_exempt
def join_request_status(request, idea_id):
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    idea = Idea.objects(id=idea_id, status="approved").first()
    if not idea:
        return JsonResponse({"status": "error", "message": "Fikir bulunamadı"}, status=404)
    jr = JoinRequest.objects(idea=idea, user=user).first()
    if jr:
        return JsonResponse({"has_applied": True, "status": jr.status})
    else:
        return JsonResponse({"has_applied": False})

@csrf_exempt
def admin_list_join_requests(request):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    status_param = request.GET.get('status')
    q = {}
    if status_param:
        q['status'] = status_param
    join_requests = JoinRequest.objects(**q)
    data = [{
        'id': str(jr.id),
        'idea_id': str(jr.idea.id),
        'user_id': str(jr.user.id),
        'user_name': jr.user.full_name,
        'note': jr.note,
        'status': jr.status,
        'created_at': str(jr.created_at),
        'admin_note': getattr(jr, 'admin_note', None)
    } for jr in join_requests]
    return JsonResponse({'status': 'ok', 'join_requests': data})

@csrf_exempt
def admin_approve_join_request(request, id):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    jr = JoinRequest.objects(id=id).first()
    if not jr or jr.status != "pending":
        return JsonResponse({'status': 'error', 'message': 'Başvuru bulunamadı veya zaten işlenmiş'}, status=404)
    jr.status = "approved"
    jr.admin_note = json.loads(request.body).get("admin_note") if request.body else None
    jr.save()
    return JsonResponse({'status': 'ok', 'message': 'Başvuru onaylandı'})

@csrf_exempt
def admin_reject_join_request(request, id):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    jr = JoinRequest.objects(id=id).first()
    if not jr or jr.status != "pending":
        return JsonResponse({'status': 'error', 'message': 'Başvuru bulunamadı veya zaten işlenmiş'}, status=404)
    data = json.loads(request.body) if request.body else {}
    jr.status = "rejected"
    jr.admin_note = data.get("admin_note")
    jr.save()
    return JsonResponse({'status': 'ok', 'message': 'Başvuru reddedildi'})
