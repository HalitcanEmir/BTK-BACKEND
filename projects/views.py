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
        # Sadece tamamlanmış projeleri getir
        projects = Project.objects(is_completed=True)
        print(f"DEBUG: Found {projects.count()} completed projects")
    else:
        # Aktif projeleri getir (tamamlanmamış ve onaylanmış)
        projects = Project.objects(is_approved=True, is_completed=False)
        print(f"DEBUG: Found {projects.count()} active projects")
    
    data = []
    for project in projects:
        project_data = {
            'id': str(project.id),
            'title': getattr(project, 'title', None),
            'description': getattr(project, 'description', None),
            'team': getattr(project, 'team', []),  # varsa
            'completed_at': project.completed_at.isoformat() if project.completed_at else None,
            'success_label': getattr(project, 'success_label', None),
            'cover_image': getattr(project, 'cover_image', None),  # opsiyonel
            'story': getattr(project, 'story', None),  # opsiyonel
            'is_completed': project.is_completed,  # Debug için ekle
        }
        data.append(project_data)
        print(f"DEBUG: Project {project.title} - is_completed: {project.is_completed}")
    
    return JsonResponse({'projects': data})

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
    project.is_completed = True
    project.completed_at = datetime.utcnow()
    project.save()
    return JsonResponse({'status': 'ok', 'message': 'Proje başarıyla tamamlandı'})

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
                project.is_completed = True
                project.completed_at = datetime.utcnow()
                project.save()
                
                return JsonResponse({'status': 'ok', 'message': 'Proje tamamlama isteği onaylandı'})
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
