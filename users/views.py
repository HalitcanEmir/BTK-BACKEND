from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
import json
from .models import User
from .utils import hash_password, check_password
import jwt
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.conf import settings

# Create your views here.

# Giriş Yap
# POST /api/auth/login
# Açıklama: Kullanıcı giriş endpointi (magic link veya şifreli)
@csrf_exempt
# Kullanıcı girişi
# POST /api/auth/login
# Body: {"email": ..., "password": ...}
# Response örneği: {"status": "ok", "jwt": "...", "user": {...}}
def login(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    user = User.objects(email=email).first()
    if not user or not check_password(password, user.password_hash):
        return JsonResponse({'status': 'error', 'message': 'E-posta veya şifre hatalı'})
    # JWT üret
    payload = {
        'email': user.email,
        'user_type': user.user_type,
        'exp': timezone.now() + timezone.timedelta(days=7)
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    user_data = {
        'email': user.email,
        'full_name': user.full_name,
        'user_type': user.user_type,
        'github_verified': user.github_verified,
        'linkedin_verified': user.linkedin_verified,
        'can_invest': user.can_invest,
        'created_at': str(user.created_at)
    }
    return JsonResponse({'status': 'ok', 'jwt': token, 'user': user_data})

# Kayıt Ol
# POST /api/auth/register
# Açıklama: Yeni kullanıcı kaydı
@csrf_exempt
# Kullanıcı kaydı
# POST /api/auth/register
# Body: {"email": ..., "password": ..., "full_name": ..., "user_type": [...], "github_token": ..., "linkedin_token": ..., "card_token": ...}
# Response örneği: {"status": "ok", "jwt": "...", "user": {...}}
def register(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        user_type = data.get('user_type', [])
        github_token = data.get('github_token')
        linkedin_token = data.get('linkedin_token')
        card_token = data.get('card_token')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    if not email or not password or not user_type:
        return JsonResponse({'status': 'error', 'message': 'Zorunlu alanlar eksik'})
    if User.objects(email=email).first():
        return JsonResponse({'status': 'error', 'message': 'Bu e-posta ile kayıtlı kullanıcı var'})
    # Şifreyi hashle
    password_hash = hash_password(password)
    # Doğrulama alanları
    github_verified = False
    linkedin_verified = False
    can_invest = False
    # Geliştirici ise token doğrulama (mock)
    if 'developer' in user_type:
        github_verified = bool(github_token)
        linkedin_verified = bool(linkedin_token)
    # Yatırımcı ise kart doğrulama (mock)
    if 'investor' in user_type:
        can_invest = bool(card_token)
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        user_type=user_type,
        github_verified=github_verified,
        linkedin_verified=linkedin_verified,
        can_invest=can_invest,
        created_at=timezone.now()
    )
    user.save()
    # JWT üret
    payload = {
        'email': user.email,
        'user_type': user.user_type,
        'exp': timezone.now() + timezone.timedelta(days=7)
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    user_data = {
        'email': user.email,
        'full_name': user.full_name,
        'user_type': user.user_type,
        'github_verified': user.github_verified,
        'linkedin_verified': user.linkedin_verified,
        'can_invest': user.can_invest,
        'created_at': str(user.created_at)
    }
    return JsonResponse({'status': 'ok', 'jwt': token, 'user': user_data})

# E-posta Doğrulama
# GET /api/auth/verify-email
# Açıklama: E-posta doğrulama endpointi

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def reset_password_request(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
    try:
        data = json.loads(request.body)
        email = data.get("email")
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    user = User.objects(email=email).first()
    if user:
        token = get_random_string(64)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        user.save()
        reset_link = f"{settings.SITE_URL}/api/auth/reset-password-confirm/{token}/"
        send_mail(
            "Şifre Sıfırlama",
            f"Şifrenizi sıfırlamak için bu linke tıklayın: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
    return JsonResponse({'status': 'ok', 'message': 'Eğer e-posta kayıtlıysa, sıfırlama linki gönderildi.'})    @csrf_exempt
    def reset_password_confirm(request, token):
        if request.method != "POST":
            return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
        try:
            data = json.loads(request.body)
            new_password = data.get("password")
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
        user = User.objects(reset_token=token, reset_token_expiry__gte=datetime.utcnow()).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Token geçersiz veya süresi dolmuş'})
        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.save()
        return JsonResponse({'status': 'ok', 'message': 'Şifreniz başarıyla değiştirildi.'})
def verify_email(request):
    return JsonResponse({"message": "E-posta Doğrulama"})

# Şifre Sıfırlama
# POST /api/auth/reset-password
# Açıklama: Şifre sıfırlama endpointi
def reset_password(request):
    return JsonResponse({"message": "Şifre Sıfırlama"})

# Kendi Profilim
# GET /api/users/me
# Açıklama: Giriş yapan kullanıcının profilini getirir
def my_profile(request):
    return JsonResponse({"message": "Kendi Profilim"})

# Başka Kullanıcının Profili
# GET /api/users/<id>
# Açıklama: Başka bir kullanıcının profilini getirir
def user_profile(request, id):
    return JsonResponse({"message": f"Kullanıcı Profili: {id}"})

# Profil Düzenleme
# PATCH /api/users/me
# Açıklama: Kendi profilini günceller
def edit_profile(request):
    return JsonResponse({"message": "Profil Düzenleme"})

# Rol Ayarları
# PATCH /api/users/roles
# Açıklama: Kullanıcı rol ayarlarını günceller
def edit_roles(request):
    return JsonResponse({"message": "Rol Ayarları"})

@csrf_exempt
def reset_password_confirm(request, token):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
    try:
        data = json.loads(request.body)
        new_password = data.get("password")
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    user = User.objects(reset_token=token, reset_token_expiry__gte=datetime.utcnow()).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Token geçersiz veya süresi dolmuş'})
    user.password_hash = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    user.save()
    return JsonResponse({'status': 'ok', 'message': 'Şifreniz başarıyla değiştirildi.'})