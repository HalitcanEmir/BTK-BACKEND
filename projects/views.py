from django.shortcuts import render
from django.http import JsonResponse
from .models import Project, ProjectCompletionRequest
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from bson import ObjectId
from users.models import User
from ideas.views import get_user_from_jwt
import json
from .models import InvestmentOffer
from .models import ProjectLike
from .utils import analyze_project, generate_project_suggestions, get_investment_advice
from ideas.models import JoinRequest
import requests
import json
from datetime import datetime, timedelta
from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine import DoesNotExist
from users.models import User
from ideas.models import JoinRequest
from .models import Project, ProjectTask, TaskLog

# Create your views here.

# Geliştirilen Projeler Sayfası
# GET /api/projects/
# Açıklama: Tüm projeleri listeler
def projects_list(request):
    return JsonResponse({"message": "Geliştirilen Projeler Sayfası"})

# Proje Detay Sayfası
# GET /api/projects/<id>
# Açıklama: Belirli bir projenin detayını getirir
@csrf_exempt
def project_detail(request, id):
    user = get_user_from_jwt(request)
    print(f"DEBUG: User from JWT: {user.full_name if user else 'None'}")
    print(f"DEBUG: User type: {getattr(user, 'user_type', []) if user else 'None'}")
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Kullanıcı rollerini belirle
    is_project_owner = user and project.project_owner == user
    is_team_member = user and user in project.team_members
    is_investor = user and 'investor' in getattr(user, 'user_type', [])
    is_developer = user and 'developer' in getattr(user, 'user_type', [])
    is_admin_user = user and is_admin(user)
    
    print(f"DEBUG: is_investor: {is_investor}")
    print(f"DEBUG: is_project_owner: {is_project_owner}")
    print(f"DEBUG: is_admin_user: {is_admin_user}")
    
    # Proje detayları
    project_data = {
        'id': str(project.id),
        'title': project.title,
        'description': getattr(project, 'description', ''),
        'category': getattr(project, 'category', ''),
        'status': project.status,
        'is_completed': project.is_completed,
        'is_approved': project.is_approved,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'completed_at': project.completed_at.isoformat() if project.completed_at else None,
        'target_amount': getattr(project, 'target_amount', 0),
        'current_amount': getattr(project, 'current_amount', 0),
        'live_stream_url': getattr(project, 'live_stream_url', ''),
        'share_url': getattr(project, 'share_url', ''),
        'team_size': len(project.team_members) if project.team_members else 0,
        'supporters_count': len(project.supporters) if project.supporters else 0,
        'can_invest': bool(is_investor),  # Tamamlanmış projelere de yatırım yapılabilir
        'can_join': bool(is_developer and not is_team_member and not project.is_completed),
        'can_manage': bool(is_project_owner or is_admin_user),
        'can_chat': bool(is_team_member or is_project_owner or is_admin_user),
        'like_count': len(project.likes) if project.likes else 0,
        'user_liked': False,  # Varsayılan değer
    }
    
    # Kullanıcının projeyi beğenip beğenmediğini kontrol et
    if user and project.likes:
        for like in project.likes:
            if like.user == user:
                project_data['user_liked'] = True
                break
    
    # Takım üyeleri
    if project.team_members:
        project_data['team_members'] = [
            {
                'id': str(member.id),
                'name': member.full_name,
                'email': member.email,
                'user_type': member.user_type
            }
            for member in project.team_members
        ]
    
    # Proje sahibi bilgileri
    if project.project_owner:
        project_data['project_owner'] = {
            'id': str(project.project_owner.id),
            'name': project.project_owner.full_name,
            'email': project.project_owner.email
        }
    
    # Yatırımcı için: Bekleyen yatırım tekliflerini göster
    if (is_project_owner or is_admin_user) and project.investment_offers:
        pending_offers = []
        for i, offer in enumerate(project.investment_offers):
            if offer.status == 'pending':
                pending_offers.append({
                    'offer_id': str(i),
                    'investor_id': str(offer.investor.id),
                    'investor_name': offer.investor.full_name,
                    'amount': offer.amount,
                    'description': offer.description,
                    'offered_at': offer.offered_at.isoformat()
                })
        if pending_offers:
            project_data['pending_investment_offers'] = pending_offers
    
    # Kullanıcının kendi yatırım tekliflerini göster
    if user and project.investment_offers:
        user_offers = []
        for i, offer in enumerate(project.investment_offers):
            if offer.investor == user:
                user_offers.append({
                    'offer_id': str(i),
                    'amount': offer.amount,
                    'description': offer.description,
                    'status': offer.status,
                    'offered_at': offer.offered_at.isoformat(),
                    'responded_at': offer.responded_at.isoformat() if offer.responded_at else None,
                    'response_note': offer.response_note
                })
        if user_offers:
            project_data['user_investment_offers'] = user_offers
    
    # Tüm yatırım tekliflerini göster (herkes için)
    if project.investment_offers:
        all_offers = []
        for i, offer in enumerate(project.investment_offers):
            all_offers.append({
                'offer_id': str(i),
                'investor_name': offer.investor.full_name,
                'amount': offer.amount,
                'description': offer.description,
                'status': offer.status,
                'offered_at': offer.offered_at.isoformat(),
                'responded_at': offer.responded_at.isoformat() if offer.responded_at else None,
                'response_note': offer.response_note
            })
        project_data['all_investment_offers'] = all_offers
    
    return JsonResponse({
        'status': 'ok',
        'project': project_data
    })

# Geliştirici Bulma / İlan Listesi
# GET /api/projects/jobs
# Açıklama: Geliştirici ilanlarını listeler
def jobs_list(request):
    return JsonResponse({"message": "Geliştirici İlan Listesi"})

# Geliştirici İlan Detay Sayfası
# GET /api/projects/jobs/<id>
# Açıklama: Geliştirici ilan detayını getirir
def job_detail(request, id):
    return JsonResponse({"message": f"Geliştirici İlan Detay Sayfası: {id}"})

# Proje Ekip Paneli ve alt fonksiyonlar
# GET /api/projects/<id>/team
# Açıklama: Proje ekibini ve başvuranları gösterir
def project_team(request, id):
    return JsonResponse({"message": f"Proje Ekip Paneli: {id}"})

# POST /api/projects/<id>/team/approve
# Açıklama: Aday onaylama işlemi
def approve_candidate(request, id):
    return JsonResponse({"message": f"Aday Onaylama: {id}"})

# POST /api/projects/<id>/team/reject
# Açıklama: Aday reddetme işlemi
def reject_candidate(request, id):
    return JsonResponse({"message": f"Aday Reddetme: {id}"})

# Proje Planlama
# GET /api/projects/<id>/plan
# Açıklama: Proje planı ve yol haritası
def project_plan(request, id):
    return JsonResponse({"message": f"Proje Planlama: {id}"})

# Görev Dağılımı
# GET /api/projects/<id>/tasks
# Açıklama: Proje görev dağılımı
def project_tasks(request, id):
    return JsonResponse({"message": f"Görev Dağılımı: {id}"})

# Takım İçi Mesajlaşma
# GET /api/projects/<id>/chat
# Açıklama: Takım içi mesajlaşma paneli
def project_chat(request, id):
    return JsonResponse({"message": f"Takım İçi Mesajlaşma: {id}"})

# AI Yardımcıları Paneli
# GET /api/projects/<id>/ai
# Açıklama: AI yardımcıları paneli
def project_ai_panel(request, id):
    return JsonResponse({"message": f"AI Yardımcıları Paneli: {id}"})

@csrf_exempt
def list_active_projects(request):
    projects = Project.objects(is_approved=True, is_completed=False)
    data = []
    for p in projects:
        data.append({
            'id': str(p.id),
            'title': getattr(p, 'title', None),
            'category': getattr(p, 'category', None),
            'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None,
            'support_count': len(p.supporters) if hasattr(p, 'supporters') and p.supporters else 0,
            'team_size': len(p.team_members) if hasattr(p, 'team_members') and p.team_members else 0
        })
    return JsonResponse({'projects': data})

@csrf_exempt
def completed_projects_list(request):
    completed = request.GET.get('completed')
    print(f"DEBUG: completed parameter = {completed}")
    
    if completed == 'true':
        # Sadece tamamlanmış projeleri getir (Biten Projeler)
        projects = Project.objects(is_completed=True, status='completed')
        print(f"DEBUG: Found {projects.count()} completed projects")
        list_type = "Biten Projeler"
    else:
        # Aktif projeleri getir (tamamlanmamış ve onaylanmış)
        projects = Project.objects(is_approved=True, is_completed=False, status='active')
        print(f"DEBUG: Found {projects.count()} active projects")
        list_type = "Aktif Projeler"
    
    data = []
    for project in projects:
        project_data = {
            'id': str(project.id),
            'title': getattr(project, 'title', None),
            'description': getattr(project, 'description', None),
            'category': getattr(project, 'category', None),
            'team_size': len(project.team_members) if project.team_members else 0,
            'completed_at': project.completed_at.isoformat() if project.completed_at else None,
            'success_label': getattr(project, 'success_label', None),
            'cover_image': getattr(project, 'cover_image', None),  # opsiyonel
            'story': getattr(project, 'story', None),  # opsiyonel
            'is_completed': project.is_completed,
            'status': getattr(project, 'status', 'active'),
            'project_owner': {
                'id': str(project.project_owner.id),
                'name': project.project_owner.full_name
            } if project.project_owner else None
        }
        data.append(project_data)
        print(f"DEBUG: Project {project.title} - is_completed: {project.is_completed}, status: {project.status}")
    
    return JsonResponse({
        'list_type': list_type,
        'projects': data,
        'total_count': len(data)
    })

def is_admin(user):
    return user and ('admin' in getattr(user, 'user_type', []) or 'admin' in getattr(user, 'roles', []))

@csrf_exempt
def complete_project(request, id):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz ID'}, status=400)
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    now = datetime.utcnow()
    project.is_completed = True
    project.completed_at = now
    project.status = 'completed'  # Status'u da güncelle
    project.save()
    
    return JsonResponse({
        'status': 'ok', 
        'message': 'Proje başarıyla tamamlandı ve "Biten Projeler" listesine eklendi',
        'project_id': str(project.id),
        'completed_at': now.isoformat()
    })

# YENİ ENDPOINT'LER

# POST /api/projects/<id>/request-completion
# Açıklama: Proje tamamlama isteği gönderir
@csrf_exempt
def request_project_completion(request, id):
    if request.method not in ['POST', 'PATCH']:
        return JsonResponse({'status': 'error', 'message': 'POST veya PATCH olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Geçersiz ID: {str(e)}'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Kullanıcının bu projenin ekibinde olup olmadığını kontrol et
    if not hasattr(project, 'team_members') or not project.team_members:
        return JsonResponse({'status': 'error', 'message': 'Proje ekibi tanımlanmamış'}, status=400)
    
    # Debug için kullanıcı bilgilerini kontrol et
    user_in_team = user in project.team_members
    team_member_names = [u.full_name for u in project.team_members]
    
    if not user_in_team:
        return JsonResponse({
            'status': 'error', 
            'message': 'Bu projenin ekibinde değilsiniz',
            'debug': {
                'user_name': user.full_name,
                'user_id': str(user.id),
                'team_members': team_member_names
            }
        }, status=403)
    
    # Zaten bekleyen bir istek var mı kontrol et
    if hasattr(project, 'completion_requests') and project.completion_requests:
        for req in project.completion_requests:
            if req.requester == user and req.status == 'pending':
                return JsonResponse({'status': 'error', 'message': 'Zaten bekleyen bir isteğiniz var'}, status=400)
    
    # Yeni istek oluştur
    completion_request = ProjectCompletionRequest(
        requester=user,
        requested_at=datetime.utcnow(),
        status='pending'
    )
    
    if not hasattr(project, 'completion_requests') or not project.completion_requests:
        project.completion_requests = []
    project.completion_requests.append(completion_request)
    project.save()
    
    return JsonResponse({
        'status': 'ok', 
        'message': 'Proje tamamlama isteği gönderildi',
        'request_id': str(len(project.completion_requests) - 1)  # Index olarak kullan
    })

# GET /api/projects/completion-requests
# Açıklama: Admin için bekleyen tamamlama isteklerini listeler
@csrf_exempt
def list_completion_requests(request):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    projects = Project.objects(completion_requests__status='pending')
    requests_data = []
    
    for project in projects:
        for i, req in enumerate(project.completion_requests):
            if req.status == 'pending':
                requests_data.append({
                    'project_id': str(project.id),
                    'project_title': getattr(project, 'title', 'Başlıksız Proje'),
                    'request_id': str(i),  # Index kullan
                    'requester_id': str(req.requester.id),
                    'requester_name': req.requester.full_name,
                    'requested_at': req.requested_at.isoformat(),
                    'team_size': len(project.team_members) if project.team_members else 0
                })
    
    return JsonResponse({'requests': requests_data})

# POST /api/projects/<project_id>/completion-requests/<request_id>/approve
# Açıklama: Admin proje tamamlama isteğini onaylar
@csrf_exempt
def approve_completion_request(request, project_id, request_id):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    try:
        project = Project.objects(id=ObjectId(project_id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # İsteği index ile bul ve güncelle
    try:
        request_index = int(request_id)
        if request_index >= 0 and request_index < len(project.completion_requests):
            req = project.completion_requests[request_index]
            if req.status == 'pending':
                req.status = 'approved'
                req.admin_user = user
                req.responded_at = datetime.utcnow()
                req.admin_response = 'Proje tamamlama isteği onaylandı'
                
                # Projeyi tamamlandı olarak işaretle
                now = datetime.utcnow()
                project.is_completed = True
                project.completed_at = now
                project.status = 'completed'  # Status'u da güncelle
                project.save()
                
                return JsonResponse({
                    'status': 'ok', 
                    'message': 'Proje tamamlama isteği onaylandı ve proje "Biten Projeler" listesine eklendi',
                    'project_id': str(project.id),
                    'completed_at': now.isoformat()
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'İstek zaten işlenmiş'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'İstek bulunamadı'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz istek ID'}, status=400)

# POST /api/projects/<project_id>/completion-requests/<request_id>/reject
# Açıklama: Admin proje tamamlama isteğini reddeder
@csrf_exempt
def reject_completion_request(request, project_id, request_id):
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    try:
        project = Project.objects(id=ObjectId(project_id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # İsteği index ile bul ve güncelle
    try:
        request_index = int(request_id)
        if request_index >= 0 and request_index < len(project.completion_requests):
            req = project.completion_requests[request_index]
            if req.status == 'pending':
                req.status = 'rejected'
                req.admin_user = user
                req.responded_at = datetime.utcnow()
                req.admin_response = 'Proje tamamlama isteği reddedildi'
                project.save()
                
                return JsonResponse({'status': 'ok', 'message': 'Proje tamamlama isteği reddedildi'})
            else:
                return JsonResponse({'status': 'error', 'message': 'İstek zaten işlenmiş'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'İstek bulunamadı'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz istek ID'}, status=400)

# POST /api/projects/<id>/invest
# Açıklama: Yatırımcı projeye yatırım teklifi gönderir
@csrf_exempt
def submit_investment_offer(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    # Yatırımcı kontrolü
    if 'investor' not in getattr(user, 'user_type', []):
        return JsonResponse({'status': 'error', 'message': 'Sadece yatırımcılar yatırım yapabilir'}, status=403)
    
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        description = data.get('description', '')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    if not amount or amount <= 0:
        return JsonResponse({'status': 'error', 'message': 'Geçerli bir miktar giriniz'}, status=400)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Tamamlanmış projelere de yatırım yapılabilir
    # if project.is_completed:
    #     return JsonResponse({'status': 'error', 'message': 'Tamamlanmış projelere yatırım yapılamaz'}, status=400)
    
    # Zaten bekleyen bir teklif var mı kontrol et
    if project.investment_offers:
        for offer in project.investment_offers:
            if offer.investor == user and offer.status == 'pending':
                return JsonResponse({'status': 'error', 'message': 'Zaten bekleyen bir yatırım teklifiniz var'}, status=400)
    
    # Yeni teklif oluştur
    investment_offer = InvestmentOffer(
        investor=user,
        amount=amount,
        description=description,
        offered_at=datetime.utcnow(),
        status='pending'
    )
    
    if not project.investment_offers:
        project.investment_offers = []
    project.investment_offers.append(investment_offer)
    project.save()
    
    return JsonResponse({
        'status': 'ok',
        'message': 'Yatırım teklifi gönderildi',
        'offer_id': str(len(project.investment_offers) - 1)
    })

# POST /api/projects/<project_id>/investment-offers/<offer_id>/approve
# Açıklama: Proje sahibi yatırım teklifini onaylar
@csrf_exempt
def approve_investment_offer(request, project_id, offer_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(project_id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Proje sahibi kontrolü
    if project.project_owner != user and not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    try:
        offer_index = int(offer_id)
        if offer_index >= 0 and offer_index < len(project.investment_offers):
            offer = project.investment_offers[offer_index]
            if offer.status == 'pending':
                offer.status = 'approved'
                offer.responded_at = datetime.utcnow()
                offer.response_note = 'Yatırım teklifi onaylandı'
                
                # Proje miktarını güncelle
                project.current_amount += offer.amount
                project.save()
                
                return JsonResponse({'status': 'ok', 'message': 'Yatırım teklifi onaylandı'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Teklif zaten işlenmiş'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Teklif bulunamadı'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz teklif ID'}, status=400)

# POST /api/projects/<project_id>/investment-offers/<offer_id>/reject
# Açıklama: Proje sahibi yatırım teklifini reddeder
@csrf_exempt
def reject_investment_offer(request, project_id, offer_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(project_id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Proje sahibi kontrolü
    if project.project_owner != user and not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    try:
        offer_index = int(offer_id)
        if offer_index >= 0 and offer_index < len(project.investment_offers):
            offer = project.investment_offers[offer_index]
            if offer.status == 'pending':
                offer.status = 'rejected'
                offer.responded_at = datetime.utcnow()
                offer.response_note = 'Yatırım teklifi reddedildi'
                project.save()
                
                return JsonResponse({'status': 'ok', 'message': 'Yatırım teklifi reddedildi'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Teklif zaten işlenmiş'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Teklif bulunamadı'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz teklif ID'}, status=400)

# GET /api/leaderboard
# Açıklama: En çok beğeni alan projeleri sıralı şekilde getirir
@csrf_exempt
def leaderboard(request):
    # Tüm onaylanmış projeleri al ve beğeni sayısına göre sırala
    projects = Project.objects(is_approved=True).order_by('-likes__count')
    
    leaderboard_data = []
    for i, project in enumerate(projects, 1):
        like_count = len(project.likes) if project.likes else 0
        
        project_data = {
            'rank': i,
            'project_id': str(project.id),
            'title': project.title,
            'description': getattr(project, 'description', ''),
            'category': getattr(project, 'category', ''),
            'like_count': like_count,
            'is_completed': project.is_completed,
            'status': project.status,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'team_size': len(project.team_members) if project.team_members else 0,
            'current_amount': getattr(project, 'current_amount', 0),
            'target_amount': getattr(project, 'target_amount', 0),
        }
        
        # İlk 3 proje için özel rozetler
        if i <= 3:
            badges = ['🥇', '🥈', '🥉']
            project_data['badge'] = badges[i-1]
        
        # Proje sahibi bilgisi
        if project.project_owner:
            project_data['project_owner'] = {
                'name': project.project_owner.full_name,
                'id': str(project.project_owner.id)
            }
        
        leaderboard_data.append(project_data)
    
    return JsonResponse({
        'status': 'ok',
        'leaderboard': leaderboard_data,
        'total_projects': len(leaderboard_data)
    })

# POST /api/projects/<id>/like
# Açıklama: Projeyi beğenir veya beğenmekten vazgeçer
@csrf_exempt
def toggle_project_like(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Kullanıcının daha önce beğenip beğenmediğini kontrol et
    user_liked = False
    like_index = -1
    
    if project.likes:
        for i, like in enumerate(project.likes):
            if like.user == user:
                user_liked = True
                like_index = i
                break
    
    if user_liked:
        # Beğenmekten vazgeç
        project.likes.pop(like_index)
        project.save()
        return JsonResponse({
            'status': 'ok',
            'message': 'Proje beğenmekten vazgeçildi',
            'liked': False,
            'like_count': len(project.likes)
        })
    else:
        # Beğen
        new_like = ProjectLike(
            user=user,
            liked_at=datetime.utcnow()
        )
        
        if not project.likes:
            project.likes = []
        project.likes.append(new_like)
        project.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Proje beğenildi',
            'liked': True,
            'like_count': len(project.likes)
        })

# AI ENDPOINT'LERİ

# POST /api/projects/<id>/analyze
# Açıklama: AI ile proje analizi yapar
@csrf_exempt
def analyze_project_ai(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Proje verilerini hazırla
    project_data = {
        'title': project.title,
        'description': getattr(project, 'description', ''),
        'category': getattr(project, 'category', ''),
        'team_size': len(project.team_members) if project.team_members else 0,
        'target_amount': getattr(project, 'target_amount', 0),
        'current_amount': getattr(project, 'current_amount', 0),
        'like_count': len(project.likes) if project.likes else 0,
        'is_completed': project.is_completed,
        'status': project.status
    }
    
    # AI analizi yap
    ai_analysis = analyze_project(project_data)
    
    return JsonResponse({
        'status': 'ok',
        'project_id': str(project.id),
        'project_title': project.title,
        'ai_analysis': ai_analysis
    })

# POST /api/projects/<id>/investment-advice
# Açıklama: Yatırım tavsiyesi alır
@csrf_exempt
def get_project_investment_advice(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    # Yatırımcı kontrolü
    if 'investor' not in getattr(user, 'user_type', []):
        return JsonResponse({'status': 'error', 'message': 'Sadece yatırımcılar yatırım tavsiyesi alabilir'}, status=403)
    
    try:
        data = json.loads(request.body)
        investor_profile = data.get('investor_profile', {})
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz proje ID'}, status=400)
    
    if not project:
        return JsonResponse({'status': 'error', 'message': 'Proje bulunamadı'}, status=404)
    
    # Proje verilerini hazırla
    project_data = {
        'title': project.title,
        'description': getattr(project, 'description', ''),
        'category': getattr(project, 'category', ''),
        'target_amount': getattr(project, 'target_amount', 0),
        'current_amount': getattr(project, 'current_amount', 0),
        'like_count': len(project.likes) if project.likes else 0,
        'team_size': len(project.team_members) if project.team_members else 0
    }
    
    # AI yatırım tavsiyesi al
    investment_advice = get_investment_advice(project_data, investor_profile)
    
    return JsonResponse({
        'status': 'ok',
        'project_id': str(project.id),
        'project_title': project.title,
        'investment_advice': investment_advice
    })

# POST /api/users/suggestions
# Açıklama: Kullanıcı için proje önerileri üretir
@csrf_exempt
def get_user_project_suggestions(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    try:
        data = json.loads(request.body)
        user_profile = data.get('user_profile', {})
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    # Kullanıcı profiline kullanıcı bilgilerini ekle
    user_profile.update({
        'user_type': getattr(user, 'user_type', []),
        'full_name': user.full_name,
        'email': user.email
    })
    
    # AI proje önerileri üret
    suggestions = generate_project_suggestions(user_profile)
    
    return JsonResponse({
        'status': 'ok',
        'user_id': str(user.id),
        'user_name': user.full_name,
        'suggestions': suggestions
    })

# PROJE BAŞVURU FONKSİYONLARI

@csrf_exempt
def project_join_request(request, id):
    """Projeye katılım başvurusu gönderir"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        data = json.loads(request.body)
        message = data.get("message", "")
        daily_available_hours = data.get("daily_available_hours")
        
        # Günlük çalışma saati validasyonu
        if daily_available_hours is None:
            return JsonResponse({"status": "error", "message": "Günlük çalışma saati belirtmelisiniz"}, status=400)
        
        try:
            daily_available_hours = int(daily_available_hours)
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "Günlük çalışma saati sayı olmalıdır"}, status=400)
        
        if daily_available_hours < 1 or daily_available_hours > 12:
            return JsonResponse({"status": "error", "message": "Günlük çalışma saati 1-12 saat arasında olmalıdır"}, status=400)
            
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)

    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz proje ID"}, status=400)
    
    if not project:
        return JsonResponse({"status": "error", "message": "Proje bulunamadı"}, status=404)
    
    if project.is_completed:
        return JsonResponse({"status": "error", "message": "Bu proje tamamlanmış, başvuru kabul edilmiyor"}, status=400)
    
    # Kullanıcı zaten ekip üyesi mi?
    if user in project.team_members:
        return JsonResponse({"status": "error", "message": "Zaten bu projenin ekibindesiniz"}, status=400)
    
    # Zaten başvuru yapmış mı?
    existing_request = JoinRequest.objects(idea=None, project=project, user=user).first()
    if existing_request:
        # Mevcut başvuruyu güncelle
        existing_request.message = message
        existing_request.daily_available_hours = daily_available_hours
        existing_request.save()
        
        return JsonResponse({
            "status": "ok", 
            "message": "Proje başvurunuz güncellendi",
            "request_id": str(existing_request.id)
        })

    # Yeni başvuru oluştur
    join_request = JoinRequest(
        idea=None,  # Fikir değil, proje başvurusu
        project=project,
        user=user,
        message=message,
        daily_available_hours=daily_available_hours
    )
    join_request.save()
    
    return JsonResponse({
        "status": "ok", 
        "message": "Proje başvurunuz alındı",
        "request_id": str(join_request.id)
    })

@csrf_exempt
def project_join_request_status(request, id):
    """Kullanıcının proje başvuru durumunu kontrol eder"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz proje ID"}, status=400)
    
    if not project:
        return JsonResponse({"status": "error", "message": "Proje bulunamadı"}, status=404)
    
    # Kullanıcı zaten ekip üyesi mi?
    if user in project.team_members:
        return JsonResponse({
            "has_applied": True, 
            "status": "approved",
            "message": "Proje ekibindesiniz"
        })
    
    # Başvuru var mı?
    join_request = JoinRequest.objects(idea=None, project=project, user=user).first()
    if join_request:
        return JsonResponse({
            "has_applied": True, 
            "status": join_request.status,
            "message": join_request.message,
            "daily_available_hours": join_request.daily_available_hours
        })
    else:
        return JsonResponse({"has_applied": False})

@csrf_exempt
def admin_list_project_join_requests(request):
    """Admin için proje başvurularını listeler"""
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    status_param = request.GET.get('status')
    q = {'idea': None}  # Sadece proje başvuruları
    if status_param:
        q['status'] = status_param
    
    join_requests = JoinRequest.objects(**q)
    data = []
    
    for jr in join_requests:
        if jr.project:  # Proje başvurusu ise
            data.append({
                'id': str(jr.id),
                'project_id': str(jr.project.id),
                'project_title': jr.project.title,
                'user_id': str(jr.user.id),
                'user_name': jr.user.full_name,
                'message': jr.message,
                'daily_available_hours': jr.daily_available_hours,
                'status': jr.status,
                'created_at': str(jr.created_at)
            })
    
    return JsonResponse({
        'status': 'ok', 
        'join_requests': data,
        'total_count': len(data)
    })

@csrf_exempt
def admin_approve_project_join_request(request, request_id):
    """Admin proje başvurusunu onaylar"""
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    try:
        join_request = JoinRequest.objects(id=ObjectId(request_id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz başvuru ID'}, status=400)
    
    if not join_request or join_request.idea:  # Fikir başvurusu ise
        return JsonResponse({'status': 'error', 'message': 'Proje başvurusu bulunamadı'}, status=404)
    
    if join_request.status != 'pending':
        return JsonResponse({'status': 'error', 'message': 'Bu başvuru zaten işlenmiş'}, status=400)
    
    # Başvuruyu onayla
    join_request.status = 'approved'
    join_request.approved_by = user
    join_request.approved_at = datetime.utcnow()
    join_request.save()
    
    # Kullanıcıyı proje ekibine ekle
    project = join_request.project
    if not project.team_members:
        project.team_members = []
    project.team_members.append(join_request.user)
    project.save()
    
    return JsonResponse({
        'status': 'ok', 
        'message': 'Proje başvurusu onaylandı ve kullanıcı ekibe eklendi',
        'user_name': join_request.user.full_name,
        'project_title': project.title
    })

@csrf_exempt
def admin_reject_project_join_request(request, request_id):
    """Admin proje başvurusunu reddeder"""
    user = get_user_from_jwt(request)
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    try:
        join_request = JoinRequest.objects(id=ObjectId(request_id)).first()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz başvuru ID'}, status=400)
    
    if not join_request or join_request.idea:  # Fikir başvurusu ise
        return JsonResponse({'status': 'error', 'message': 'Proje başvurusu bulunamadı'}, status=404)
    
    if join_request.status != 'pending':
        return JsonResponse({'status': 'error', 'message': 'Bu başvuru zaten işlenmiş'}, status=400)
    
    # Başvuruyu reddet
    join_request.status = 'rejected'
    join_request.approved_by = user
    join_request.approved_at = datetime.utcnow()
    join_request.save()
    
    return JsonResponse({
        'status': 'ok', 
        'message': 'Proje başvurusu reddedildi',
        'user_name': join_request.user.full_name,
        'project_title': join_request.project.title
    })

# PROJE SOHBET FONKSİYONLARI

@csrf_exempt
def project_chat(request, id):
    """Proje sohbeti - mesaj gönderme ve alma"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz proje ID"}, status=400)
    
    if not project:
        return JsonResponse({"status": "error", "message": "Proje bulunamadı"}, status=404)
    
    # Kullanıcının bu projeye katılım yetkisi var mı kontrol et
    is_project_owner = project.project_owner == user
    is_team_member = user in project.team_members if project.team_members else False
    is_admin_user = is_admin(user)
    
    if not (is_project_owner or is_team_member or is_admin_user):
        return JsonResponse({"status": "error", "message": "Bu projeye erişim yetkiniz yok"}, status=403)
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
            if not content:
                return JsonResponse({"status": "error", "message": "Mesaj boş olamaz"}, status=400)
        except Exception:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
        
        # Mesajı kaydet
        from ideas.models import ProjectMessage
        ProjectMessage(project=project, user=user, content=content).save()
        return JsonResponse({"status": "ok", "message": "Mesaj gönderildi"})
    
    elif request.method == "GET":
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 20))
        
        from ideas.models import ProjectMessage
        messages = ProjectMessage.objects(project=project).order_by("-timestamp").skip((page-1)*limit).limit(limit)
        data = [{
            "id": str(msg.id),
            "sender": {
                "id": str(msg.user.id),
                "name": msg.user.full_name
            },
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        } for msg in messages]
        return JsonResponse({"messages": data})
    
    else:
        return JsonResponse({"status": "error", "message": "Yöntem desteklenmiyor"}, status=405)

@csrf_exempt
def get_project_team_planning_data(request, id):
    """Proje ekibi planlaması için Gemini'ye gönderilecek veriyi hazırlar"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz proje ID"}, status=400)
    
    if not project:
        return JsonResponse({"status": "error", "message": "Proje bulunamadı"}, status=404)
    
    # Onaylanmış başvuruları al
    approved_requests = JoinRequest.objects(
        project=project,
        status='approved'
    )
    
    team_data = []
    for req in approved_requests:
        team_data.append({
            'user_id': str(req.user.id),
            'user_name': req.user.full_name,
            'daily_available_hours': req.daily_available_hours,
            'message': req.message
        })
    
    # Proje bilgileri
    project_data = {
        'project_id': str(project.id),
        'project_title': project.title,
        'project_description': project.description,
        'team_members': team_data,
        'total_team_size': len(team_data),
        'total_daily_hours': sum(member['daily_available_hours'] for member in team_data)
    }
    
    return JsonResponse({
        'status': 'ok',
        'project_data': project_data,
        'message': 'Proje ekibi planlaması için veri hazırlandı'
    })

@csrf_exempt
def project_join_request_cancel(request, id):
    """Kullanıcının proje başvurusunu iptal eder"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz proje ID"}, status=400)
    
    if not project:
        return JsonResponse({"status": "error", "message": "Proje bulunamadı"}, status=404)
    
    # Başvuru var mı?
    existing_request = JoinRequest.objects(idea=None, project=project, user=user).first()
    if not existing_request:
        return JsonResponse({"status": "error", "message": "Bu projeye başvurunuz bulunamadı"}, status=404)
    
    # Başvuru zaten onaylanmış mı?
    if existing_request.status == 'approved':
        return JsonResponse({"status": "error", "message": "Onaylanmış başvuru iptal edilemez"}, status=400)
    
    # Başvuruyu sil
    existing_request.delete()
    
    return JsonResponse({
        "status": "ok", 
        "message": "Proje başvurunuz iptal edildi"
    })

@csrf_exempt
def generate_project_tasks_with_gemini(request, id):
    """Gemini AI ile proje görevlerini oluşturur"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    if not is_admin(user):
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz proje ID"}, status=400)
    
    if not project:
        return JsonResponse({"status": "error", "message": "Proje bulunamadı"}, status=404)
    
    # Onaylanmış başvuruları al
    approved_requests = JoinRequest.objects(
        project=project,
        status='approved'
    )
    
    if not approved_requests:
        return JsonResponse({"status": "error", "message": "Bu proje için onaylanmış başvuru bulunamadı"}, status=400)
    
    # Ekip üyeleri verilerini hazırla
    team_members = []
    for req in approved_requests:
        # Kullanıcının yeteneklerini al (CV analizi sonucu veya kayıt sırasında)
        user_skills = getattr(req.user, 'known_technologies', []) or []
        
        # Rol tercihini belirle (başvuru mesajından çıkar)
        role = determine_role_from_message(req.message)
        
        team_members.append({
            "name": req.user.full_name,
            "role": role,
            "available_hours": req.daily_available_hours,
            "skills": user_skills
        })
    
    # Gemini'ye gönderilecek prompt verisi
    gemini_data = {
        "project_name": project.title,
        "project_description": project.description,
        "team_members": team_members,
        "project_needs": project.description
    }
    
    # Gemini AI'ya gönder
    try:
        gemini_response = send_to_gemini_for_task_planning(gemini_data)
        
        if gemini_response.get('status') == 'success':
            # Görevleri veritabanına kaydet
            tasks_created = save_tasks_to_database(project, gemini_response['tasks'], user)
            
            return JsonResponse({
                "status": "ok",
                "message": f"{tasks_created} görev başarıyla oluşturuldu",
                "tasks": gemini_response['tasks'],
                "total_tasks": tasks_created
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Gemini AI'dan yanıt alınamadı",
                "error": gemini_response.get('error', 'Bilinmeyen hata')
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "Görev planlaması sırasında hata oluştu",
            "error": str(e)
        }, status=500)

def determine_role_from_message(message):
    """Başvuru mesajından rol tercihini belirler"""
    message_lower = message.lower() if message else ""
    
    if any(word in message_lower for word in ['frontend', 'react', 'vue', 'angular', 'html', 'css', 'javascript']):
        return "frontend"
    elif any(word in message_lower for word in ['backend', 'python', 'django', 'nodejs', 'java', 'php', 'api']):
        return "backend"
    elif any(word in message_lower for word in ['test', 'qa', 'testing', 'quality']):
        return "test"
    else:
        return "general"  # Genel rol

def send_to_gemini_for_task_planning(data):
    """Gemini AI'ya görev planlaması için veri gönderir"""
    import google.generativeai as genai
    import json
    import re
    from django.conf import settings
    
    def clean_gemini_json(raw_text):
        """Gemini'den dönen cevaptaki kod bloğu işaretlerini temizle"""
        cleaned = re.sub(r"^```json|^```|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
        return cleaned
    
    try:
        # Gemini AI'yı yapılandır (mevcut settings'den al)
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt hazırla
        prompt = f"""
        Sen bir proje yöneticisisin. Aşağıdaki proje ve ekip bilgilerine göre detaylı görev planlaması yap.

        PROJE BİLGİLERİ:
        - Proje Adı: {data['project_name']}
        - Proje Açıklaması: {data['project_description']}
        - Proje İhtiyaçları: {data['project_needs']}

        EKİP ÜYELERİ:
        """
        
        for member in data['team_members']:
            prompt += f"""
        - {member['name']}:
          * Rol: {member['role']}
          * Günlük Çalışma Saati: {member['available_hours']} saat
          * Yetenekler: {', '.join(member['skills']) if member['skills'] else 'Belirtilmemiş'}
            """
        
        prompt += f"""

        GÖREV:
        Bu proje için detaylı görev planlaması yap. Her görev için:
        1. Görev başlığı (açık ve anlaşılır)
        2. Hangi kişiye atanacağı
        3. Tahmini süre (gün olarak)
        4. Başlangıç ve bitiş tarihi
        5. Görev açıklaması
        6. Öncelik seviyesi (low, medium, high, urgent)

        KURALLAR:
        - Görevler mantıklı sırayla olmalı (önce backend, sonra frontend)
        - Her kişinin günlük çalışma saatine göre süre hesapla
        - Görevler 1-14 gün arasında olmalı
        - Tarihler YYYY-MM-DD formatında olmalı
        - Bugünden başla (bugün: {datetime.now().strftime('%Y-%m-%d')})

        SADECE JSON formatında yanıtla, başka açıklama ekleme:

        {{
          "tasks": [
            {{
              "title": "Görev başlığı",
              "assigned_to": "Kullanıcı adı",
              "duration_days": 3,
              "start_date": "2025-07-28",
              "end_date": "2025-07-31",
              "description": "Detaylı görev açıklaması",
              "priority": "medium"
            }}
          ]
        }}
        """
        
        # Gemini'ye gönder
        response = model.generate_content(prompt)
        
        if not response.text or response.text.strip() == "":
            return {
                "status": "error",
                "error": "Gemini boş cevap döndü"
            }
        
        # Response'u parse et
        try:
            cleaned_text = clean_gemini_json(response.text)
            tasks_data = json.loads(cleaned_text)
            
            return {
                "status": "success",
                "tasks": tasks_data.get("tasks", [])
            }
            
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error": f"Gemini'den gelen yanıt JSON formatında değil: {str(e)}",
                "raw_response": response.text[:500]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": f"Gemini API hatası: {str(e)}"
        }

def save_tasks_to_database(project, tasks, admin_user):
    """Gemini'den gelen görevleri veritabanına kaydeder"""
    tasks_created = 0
    
    for task_data in tasks:
        try:
            # Kullanıcıyı bul
            assigned_user = User.objects(full_name=task_data['assigned_to']).first()
            if not assigned_user:
                continue
            
            # Tarihleri parse et
            start_date = datetime.strptime(task_data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(task_data['end_date'], '%Y-%m-%d')
            
            # Görevi oluştur
            task = ProjectTask(
                project=project,
                title=task_data['title'],
                description=task_data.get('description', ''),
                assigned_user=assigned_user,
                assigned_by=admin_user,
                start_date=start_date,
                end_date=end_date,
                duration_days=task_data['duration_days'],
                priority=task_data.get('priority', 'medium')
            )
            task.save()
            tasks_created += 1
            
        except Exception as e:
            print(f"Görev kaydedilirken hata: {e}")
            continue
    
    return tasks_created

@csrf_exempt
def get_user_tasks(request):
    """Kullanıcının görevlerini listeler"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    # Kullanıcının görevlerini al
    query = {'assigned_user': user}
    if status_filter:
        query['status'] = status_filter
    if priority_filter:
        query['priority'] = priority_filter
    
    tasks = ProjectTask.objects(**query).order_by('end_date')
    
    tasks_data = []
    for task in tasks:
        # Görev loglarını al
        recent_logs = TaskLog.objects(task=task).order_by('-created_at')[:3]
        logs_data = []
        for log in recent_logs:
            logs_data.append({
                'action': log.action,
                'notes': log.notes,
                'created_at': str(log.created_at)
            })
        
        tasks_data.append({
            'id': str(task.id),
            'title': task.title,
            'description': task.description,
            'project_id': str(task.project.id),
            'project_title': task.project.title,
            'status': task.status,
            'priority': task.priority,
            'start_date': str(task.start_date),
            'end_date': str(task.end_date),
            'duration_days': task.duration_days,
            'assigned_by': task.assigned_by.full_name,
            'created_at': str(task.created_at),
            'completed_at': str(task.completed_at) if task.completed_at else None,
            'completion_notes': task.completion_notes,
            'recent_logs': logs_data,
            'is_overdue': task.end_date < datetime.utcnow() and task.status != 'done'
        })
    
    return JsonResponse({
        'status': 'ok',
        'tasks': tasks_data,
        'total_count': len(tasks_data)
    })

@csrf_exempt
def get_project_tasks(request, id):
    """Projenin tüm görevlerini listeler (admin için)"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        project = Project.objects(id=ObjectId(id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz proje ID"}, status=400)
    
    if not project:
        return JsonResponse({"status": "error", "message": "Proje bulunamadı"}, status=404)
    
    # Admin kontrolü veya proje sahibi kontrolü
    if not is_admin(user) and project.project_owner != user:
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    
    tasks = ProjectTask.objects(project=project).order_by('end_date')
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': str(task.id),
            'title': task.title,
            'description': task.description,
            'assigned_user_id': str(task.assigned_user.id),
            'assigned_user_name': task.assigned_user.full_name,
            'status': task.status,
            'priority': task.priority,
            'start_date': str(task.start_date),
            'end_date': str(task.end_date),
            'duration_days': task.duration_days,
            'assigned_by': task.assigned_by.full_name,
            'created_at': str(task.created_at),
            'completed_at': str(task.completed_at) if task.completed_at else None,
            'completion_notes': task.completion_notes,
            'is_overdue': task.end_date < datetime.utcnow() and task.status != 'done'
        })
    
    # İstatistikler
    total_tasks = len(tasks_data)
    completed_tasks = len([t for t in tasks_data if t['status'] == 'done'])
    overdue_tasks = len([t for t in tasks_data if t['is_overdue']])
    
    return JsonResponse({
        'status': 'ok',
        'tasks': tasks_data,
        'statistics': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': total_tasks - completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        }
    })

@csrf_exempt
def update_task_status(request, task_id):
    """Görev durumunu günceller"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        notes = data.get('notes', '')
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    if not new_status:
        return JsonResponse({"status": "error", "message": "Durum belirtmelisiniz"}, status=400)
    
    try:
        task = ProjectTask.objects(id=ObjectId(task_id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz görev ID"}, status=400)
    
    if not task:
        return JsonResponse({"status": "error", "message": "Görev bulunamadı"}, status=404)
    
    # Sadece görevi atanan kişi durumu değiştirebilir
    if task.assigned_user != user:
        return JsonResponse({"status": "error", "message": "Bu görevi sadece atanan kişi güncelleyebilir"}, status=403)
    
    old_status = task.status
    task.status = new_status
    
    # Eğer görev tamamlandıysa
    if new_status == 'done':
        task.completed_at = datetime.utcnow()
        task.completion_notes = notes
    
    task.updated_at = datetime.utcnow()
    task.save()
    
    # Log kaydı oluştur
    action = 'completed' if new_status == 'done' else 'updated'
    task_log = TaskLog(
        task=task,
        user=user,
        action=action,
        notes=notes
    )
    task_log.save()
    
    return JsonResponse({
        "status": "ok",
        "message": f"Görev durumu '{old_status}' -> '{new_status}' olarak güncellendi",
        "task_id": str(task.id),
        "new_status": new_status
    })

@csrf_exempt
def add_task_log(request, task_id):
    """Göreve log ekler"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        notes = data.get('notes', '')
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    if not action:
        return JsonResponse({"status": "error", "message": "Aksiyon belirtmelisiniz"}, status=400)
    
    try:
        task = ProjectTask.objects(id=ObjectId(task_id)).first()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz görev ID"}, status=400)
    
    if not task:
        return JsonResponse({"status": "error", "message": "Görev bulunamadı"}, status=404)
    
    # Sadece görevi atanan kişi log ekleyebilir
    if task.assigned_user != user:
        return JsonResponse({"status": "error", "message": "Bu göreve sadece atanan kişi log ekleyebilir"}, status=403)
    
    # Log kaydı oluştur
    task_log = TaskLog(
        task=task,
        user=user,
        action=action,
        notes=notes
    )
    task_log.save()
    
    return JsonResponse({
        "status": "ok",
        "message": "Log başarıyla eklendi",
        "log_id": str(task_log.id)
    })

@csrf_exempt
def get_task_notifications(request):
    """Kullanıcının görev bildirimlerini getirir"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    # Kullanıcının görevlerini al
    user_tasks = ProjectTask.objects(assigned_user=user, status__in=['to-do', 'in-progress'])
    
    notifications = []
    current_time = datetime.utcnow()
    
    for task in user_tasks:
        # Süresi geçen görevler
        if task.end_date < current_time and task.status != 'done':
            notifications.append({
                'type': 'overdue',
                'title': 'Süresi Geçen Görev',
                'message': f'"{task.title}" görevinin süresi geçti',
                'task_id': str(task.id),
                'project_title': task.project.title,
                'days_overdue': (current_time - task.end_date).days
            })
        
        # Yaklaşan görevler (2 gün içinde)
        elif task.end_date > current_time:
            days_until_deadline = (task.end_date - current_time).days
            if days_until_deadline <= 2:
                notifications.append({
                    'type': 'upcoming',
                    'title': 'Yaklaşan Görev',
                    'message': f'"{task.title}" görevinin bitiş tarihi yaklaşıyor',
                    'task_id': str(task.id),
                    'project_title': task.project.title,
                    'days_until_deadline': days_until_deadline
                })
    
    return JsonResponse({
        'status': 'ok',
        'notifications': notifications,
        'total_count': len(notifications)
    })

@csrf_exempt
def mark_notification_as_read(request, notification_id):
    """Bildirimi okundu olarak işaretler"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    # Bu örnekte basit bir yapı kullanıyoruz
    # Gerçek uygulamada Notification modeli olabilir
    
    return JsonResponse({
        "status": "ok",
        "message": "Bildirim okundu olarak işaretlendi"
    })

@csrf_exempt
def calculate_user_performance_score(request, user_id=None):
    """Kullanıcının performans skorunu hesaplar"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    # Eğer user_id belirtilmişse ve admin ise, o kullanıcının skorunu hesapla
    target_user = user
    if user_id and is_admin(user):
        try:
            target_user = User.objects(id=ObjectId(user_id)).first()
            if not target_user:
                return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı"}, status=404)
        except Exception:
            return JsonResponse({"status": "error", "message": "Geçersiz kullanıcı ID"}, status=400)
    elif user_id and not is_admin(user):
        return JsonResponse({"status": "error", "message": "Yetkisiz erişim"}, status=403)
    
    # Kullanıcının tüm görevlerini al
    user_tasks = ProjectTask.objects(assigned_user=target_user)
    
    total_tasks = len(user_tasks)
    completed_tasks = len([t for t in user_tasks if t.status == 'done'])
    overdue_tasks = len([t for t in user_tasks if t.end_date < datetime.utcnow() and t.status != 'done'])
    on_time_tasks = len([t for t in user_tasks if t.status == 'done' and t.completed_at and t.completed_at <= t.end_date])
    
    # Skor hesaplama
    base_score = 100
    
    # Tamamlanan görevler için +10 puan
    completion_bonus = completed_tasks * 10
    
    # Zamanında tamamlanan görevler için +5 puan
    on_time_bonus = on_time_tasks * 5
    
    # Geciken görevler için -15 puan
    overdue_penalty = overdue_tasks * 15
    
    # Toplam skor
    total_score = base_score + completion_bonus + on_time_bonus - overdue_penalty
    
    # Minimum 0, maksimum 1000
    total_score = max(0, min(1000, total_score))
    
    # Performans seviyesi
    if total_score >= 800:
        performance_level = "Mükemmel"
    elif total_score >= 600:
        performance_level = "İyi"
    elif total_score >= 400:
        performance_level = "Orta"
    elif total_score >= 200:
        performance_level = "Geliştirilmeli"
    else:
        performance_level = "Kritik"
    
    return JsonResponse({
        'status': 'ok',
        'user_id': str(target_user.id),
        'user_name': target_user.full_name,
        'performance_score': total_score,
        'performance_level': performance_level,
        'statistics': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'on_time_tasks': on_time_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
            'on_time_rate': round((on_time_tasks / completed_tasks * 100) if completed_tasks > 0 else 0, 2)
        },
        'score_breakdown': {
            'base_score': base_score,
            'completion_bonus': completion_bonus,
            'on_time_bonus': on_time_bonus,
            'overdue_penalty': overdue_penalty,
            'total_score': total_score
        }
    })

@csrf_exempt
def get_team_performance_leaderboard(request):
    """Ekip performans sıralamasını getirir"""
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Giriş yapmalısınız"}, status=401)
    
    # Tüm kullanıcıların performans skorlarını hesapla
    all_users = User.objects()
    leaderboard = []
    
    for user_obj in all_users:
        # Kullanıcının görevlerini al
        user_tasks = ProjectTask.objects(assigned_user=user_obj)
        
        if len(user_tasks) == 0:
            continue  # Hiç görevi olmayan kullanıcıları atla
        
        total_tasks = len(user_tasks)
        completed_tasks = len([t for t in user_tasks if t.status == 'done'])
        overdue_tasks = len([t for t in user_tasks if t.end_date < datetime.utcnow() and t.status != 'done'])
        on_time_tasks = len([t for t in user_tasks if t.status == 'done' and t.completed_at and t.completed_at <= t.end_date])
        
        # Skor hesaplama
        base_score = 100
        completion_bonus = completed_tasks * 10
        on_time_bonus = on_time_tasks * 5
        overdue_penalty = overdue_tasks * 15
        total_score = max(0, min(1000, base_score + completion_bonus + on_time_bonus - overdue_penalty))
        
        leaderboard.append({
            'user_id': str(user_obj.id),
            'user_name': user_obj.full_name,
            'performance_score': total_score,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        })
    
    # Skora göre sırala (yüksekten düşüğe)
    leaderboard.sort(key=lambda x: x['performance_score'], reverse=True)
    
    return JsonResponse({
        'status': 'ok',
        'leaderboard': leaderboard,
        'total_participants': len(leaderboard)
    })
