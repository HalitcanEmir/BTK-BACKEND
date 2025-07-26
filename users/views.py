from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
import json
from .models import User
from .utils import hash_password, check_password, analyze_id_card, scrape_linkedin_profile, analyze_linkedin_profile, verify_identity_match
import jwt
from django.conf import settings
from .forms import IDCardForm
from .utils import send_image_to_gemini
from mongoengine.errors import DoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.

def get_user_from_jwt(request):
    """
    JWT token'dan kullanıcıyı getirir
    
    Args:
        request: Django request objesi
    
    Returns:
        User objesi veya None
    """
    try:
        # Authorization header'dan token'ı al
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        # JWT'yi decode et
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Kullanıcıyı bul
        email = payload.get('email')
        if not email:
            return None
        
        user = User.objects(email=email).first()
        return user
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None

def get_user_from_token(request):
    """JWT token'dan kullanıcıyı al"""
    auth_header = request.headers.get('Authorization')
    print(f"Auth header: {auth_header}")
    if not auth_header or not auth_header.startswith('Bearer '):
        print("Auth header yok veya Bearer ile başlamıyor")
        return None
    
    token = auth_header.split(' ')[1]
    print(f"Token: {token[:20]}...")  # İlk 20 karakteri göster
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(f"Payload: {payload}")
        email = payload.get('email')  # user_id yerine email kullan
        print(f"Email: {email}")
        if email:
            user = User.objects.get(email=email)  # id yerine email ile ara
            print(f"User found: {user.email}")
            return user
        else:
            print("Email bulunamadı")
    except jwt.InvalidTokenError as e:
        print(f"JWT decode hatası: {e}")
        return None
    except DoesNotExist as e:
        print(f"User bulunamadı: {e}")
        return None
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        return None
    return None

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

# KİMLİK DOĞRULAMA ENDPOINT'LERİ

# POST /api/auth/verify-identity
# Açıklama: Kimlik kartı analizi ve LinkedIn doğrulama
@csrf_exempt
def verify_identity(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    print("🚀 VERIFY IDENTITY ENDPOINT ÇAĞRILDI!")
    print(f"📊 Request method: {request.method}")
    print(f"📊 Request headers: {dict(request.headers)}")
    
    user = get_user_from_jwt(request)
    if not user:
        print("❌ Kullanıcı bulunamadı")
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    print(f"✅ Kullanıcı bulundu: {user.email}")
    
    try:
        data = json.loads(request.body)
        id_card_image = data.get('id_card_image')  # Base64 encoded image or file path
        linkedin_url = data.get('linkedin_url')
        print(f"📁 Gelen veriler: id_card_image={id_card_image[:50]}..., linkedin_url={linkedin_url}")
    except Exception as e:
        print(f"❌ JSON parse hatası: {e}")
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    if not id_card_image or not linkedin_url:
        return JsonResponse({'status': 'error', 'message': 'Kimlik görseli ve LinkedIn URL gerekli'}, status=400)
    
    # 1. Kimlik kartı analizi
    try:
        print(f"🔍 KİMLİK ANALİZİ BAŞLATILIYOR...")
        print(f"📁 Gelen dosya: {id_card_image}")
        
        # Eğer dosya adı ise, base64'e çevir
        if not id_card_image.startswith('data:image'):
            print(f"📂 Dosya adı tespit edildi, base64'e çevriliyor...")
            # Dosya yolunu base64'e çevir
            import base64
            import os
            
            # Dosya yolunu kontrol et - hem relative hem absolute path dene
            file_paths_to_try = [
                id_card_image,  # Verilen yol
                os.path.join(os.getcwd(), id_card_image),  # Current directory + dosya adı
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', id_card_image),  # Project root
            ]
            
            print(f"🔍 Aranan dosya yolları: {file_paths_to_try}")
            
            file_found = False
            for file_path in file_paths_to_try:
                if os.path.exists(file_path):
                    print(f"✅ Dosya bulundu: {file_path}")
                    try:
                        with open(file_path, 'rb') as image_file:
                            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                            id_card_image = f"data:image/jpeg;base64,{image_data}"
                            print(f"✅ Base64 dönüşümü başarılı, uzunluk: {len(image_data)}")
                            file_found = True
                            break
                    except Exception as e:
                        print(f"❌ Dosya okuma hatası: {e}")
                        continue
            
            if not file_found:
                print(f"❌ Dosya bulunamadı!")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Kimlik görseli dosyası bulunamadı',
                    'details': f'Aranan dosya: {id_card_image}',
                    'tried_paths': file_paths_to_try,
                    'current_directory': os.getcwd()
                }, status=400)
        else:
            print(f"✅ Base64 formatında geldi, uzunluk: {len(id_card_image)}")
        
        # Base64'ten image data oluştur - DÜZELTME
        # id_card_image zaten base64 string, dict formatına çevir
        image_data = {"mime_type": "image/jpeg", "data": id_card_image}
        print(f"🔍 AI analizi başlatılıyor...")
        print(f"📊 Image data type: {type(image_data)}")
        print(f"📁 Dosya yolu: {id_card_image[:100]}...")
        
        id_analysis = analyze_id_card(image_data)
        
        print(f"📊 AI Analiz Sonucu: {id_analysis}")
        
        if id_analysis['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'Kimlik analizi başarısız',
                'details': id_analysis.get('message', 'Bilinmeyen hata'),
                'raw_response': id_analysis.get('raw_response', '')
            }, status=400)
        
        id_name = id_analysis.get('name')
        id_surname = id_analysis.get('surname')
        
        print(f"📝 Kimlikten çıkarılan: {id_name} {id_surname}")
        
        if not id_name or not id_surname:
            return JsonResponse({
                'status': 'error',
                'message': 'Kimlikten ad-soyad çıkarılamadı',
                'raw_response': id_analysis.get('raw_response', '')
            }, status=400)
        
    except Exception as e:
        print(f"❌ Kimlik analizi hatası: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Kimlik analizi hatası',
            'error': str(e)
        }, status=500)
    
    # 2. LinkedIn profil analizi
    try:
        print(f"🔗 LINKEDIN ANALİZİ BAŞLATILIYOR...")
        print(f"🌐 LinkedIn URL: {linkedin_url}")
        
        linkedin_data = scrape_linkedin_profile(linkedin_url)
        
        print(f"📊 LinkedIn Analiz Sonucu: {linkedin_data}")
        
        if linkedin_data['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'LinkedIn analizi başarısız',
                'details': linkedin_data.get('message', 'Bilinmeyen hata')
            }, status=400)
        
        linkedin_name = linkedin_data.get('name')
        linkedin_summary = linkedin_data.get('summary', '')
        
        print(f"👤 LinkedIn'den çıkarılan: {linkedin_name}")
        
    except Exception as e:
        print(f"❌ LinkedIn analizi hatası: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'LinkedIn analizi hatası',
            'error': str(e)
        }, status=500)
    
    # 3. Kimlik-LinkedIn eşleşme kontrolü
    try:
        match_result = verify_identity_match(id_name, id_surname, linkedin_name)
        
        if match_result['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'Eşleşme kontrolü başarısız',
                'details': match_result.get('message', 'Bilinmeyen hata')
            }, status=400)
        
        if not match_result['match']:
            return JsonResponse({
                'status': 'error',
                'message': 'Kimlik adınız ile LinkedIn adınız eşleşmiyor',
                'id_name': f"{id_name} {id_surname}",
                'linkedin_name': linkedin_name
            }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Eşleşme kontrolü hatası',
            'error': str(e)
        }, status=500)
    
    # 4. LinkedIn profil AI analizi
    try:
        profile_data = {
            'name': linkedin_name,
            'summary': linkedin_summary
        }
        
        ai_analysis = analyze_linkedin_profile(profile_data)
        
        if ai_analysis['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'LinkedIn AI analizi başarısız',
                'details': ai_analysis.get('message', 'Bilinmeyen hata')
            }, status=400)
        
        technical_analysis = ai_analysis.get('analysis', {})
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'LinkedIn AI analizi hatası',
            'error': str(e)
        }, status=500)
    
    # 5. Kullanıcı bilgilerini güncelle
    try:
        user.id_card_image_url = f"id_cards/{user.id}.jpg"  # Güvenli URL
        user.verified_name = id_name
        user.verified_surname = id_surname
        user.identity_verified = True
        
        user.linkedin_url = linkedin_url
        user.linkedin_name = linkedin_name
        user.linkedin_verified = True
        
        user.languages_known = json.dumps(technical_analysis.get('skills', {}))
        user.experience_estimate = technical_analysis.get('experience_estimate', '')
        user.profile_summary = technical_analysis.get('summary', '')
        user.technical_analysis = json.dumps(technical_analysis)
        
        user.verification_status = 'verified'
        user.verification_notes = f"Kimlik-LinkedIn eşleşmesi: {match_result['confidence']} güven"
        
        user.save()
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Kullanıcı bilgileri güncellenemedi',
            'error': str(e)
        }, status=500)
    
    # 6. Başarılı yanıt
    return JsonResponse({
        'status': 'ok',
        'message': 'Kimlik doğrulama başarılı',
        'verification': {
            'identity_verified': True,
            'linkedin_verified': True,
            'match_confidence': match_result['confidence'],
            'id_name': f"{id_name} {id_surname}",
            'linkedin_name': linkedin_name,
            'experience_estimate': technical_analysis.get('experience_estimate', ''),
            'skills_count': len(technical_analysis.get('skills', {}))
        }
    })

# POST /api/auth/verify-id-card
# Açıklama: Sadece kimlik kartı analizi
@csrf_exempt
def verify_id_card(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    print("🚀 VERIFY ID CARD ENDPOINT ÇAĞRILDI!")
    
    user = get_user_from_jwt(request)
    if not user:
        print("❌ Kullanıcı bulunamadı")
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    print(f"✅ Kullanıcı bulundu: {user.email}")
    
    try:
        data = json.loads(request.body)
        id_card_image = data.get('id_card_image')
    except Exception as e:
        print(f"❌ JSON parse hatası: {e}")
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    if not id_card_image:
        return JsonResponse({'status': 'error', 'message': 'Kimlik görseli gerekli'}, status=400)
    
    # Kimlik kartı analizi
    try:
        print(f"🔍 KİMLİK ANALİZİ BAŞLATILIYOR...")
        print(f"📁 Gelen dosya: {id_card_image}")
        
        # Eğer dosya adı ise, base64'e çevir
        if not id_card_image.startswith('data:image'):
            print(f"📂 Dosya adı tespit edildi, base64'e çevriliyor...")
            import base64
            import os
            
            # Dosya yolunu kontrol et
            file_paths_to_try = [
                id_card_image,
                os.path.join(os.getcwd(), id_card_image),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', id_card_image),
            ]
            
            print(f"🔍 Aranan dosya yolları: {file_paths_to_try}")
            
            file_found = False
            for file_path in file_paths_to_try:
                if os.path.exists(file_path):
                    print(f"✅ Dosya bulundu: {file_path}")
                    try:
                        with open(file_path, 'rb') as image_file:
                            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                            # Sadece base64 kısmını gönder, önek olmadan
                            id_card_image = image_data
                            print(f"✅ Base64 dönüşümü başarılı, uzunluk: {len(image_data)}")
                            file_found = True
                            break
                    except Exception as e:
                        print(f"❌ Dosya okuma hatası: {e}")
                        continue
            
            if not file_found:
                print(f"❌ Dosya bulunamadı!")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Kimlik görseli dosyası bulunamadı',
                    'details': f'Aranan dosya: {id_card_image}',
                    'tried_paths': file_paths_to_try,
                    'current_directory': os.getcwd()
                }, status=400)
        else:
            print(f"✅ Base64 formatında geldi, uzunluk: {len(id_card_image)}")
            # Eğer data:image/jpeg;base64, öneki varsa kaldır
            if id_card_image.startswith('data:image/jpeg;base64,'):
                id_card_image = id_card_image[23:]  # data:image/jpeg;base64, kısmını kaldır
                print(f"✅ Base64 öneki kaldırıldı")
        
        # AI analizi
        print(f"🔍 AI analizi başlatılıyor...")
        
        id_analysis = analyze_id_card(id_card_image)
        
        print(f"📊 AI Analiz Sonucu: {id_analysis}")
        
        if id_analysis['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'Kimlik analizi başarısız',
                'details': id_analysis.get('message', 'Bilinmeyen hata'),
                'raw_response': id_analysis.get('raw_response', '')
            }, status=400)
        
        id_name = id_analysis.get('name')
        id_surname = id_analysis.get('surname')
        
        print(f"📝 Kimlikten çıkarılan: {id_name} {id_surname}")
        
        if not id_name or not id_surname:
            return JsonResponse({
                'status': 'error',
                'message': 'Kimlikten ad-soyad çıkarılamadı',
                'raw_response': id_analysis.get('raw_response', '')
            }, status=400)
        
        # Kullanıcı bilgilerini güncelle
        user.id_card_image_url = f"id_cards/{user.id}.jpg"
        user.verified_name = id_name
        user.verified_surname = id_surname
        user.identity_verified = True
        user.verification_status = 'id_verified'  # Yeni durum
        user.verification_notes = "Kimlik doğrulandı, LinkedIn bekleniyor"
        user.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Kimlik doğrulama başarılı',
            'verification': {
                'identity_verified': True,
                'id_name': f"{id_name} {id_surname}",
                'next_step': 'linkedin_verification'
            }
        })
        
    except Exception as e:
        print(f"❌ Kimlik analizi hatası: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Kimlik analizi hatası',
            'error': str(e)
        }, status=500)

# POST /api/auth/verify-linkedin
# Açıklama: LinkedIn doğrulama (kimlik doğrulandıktan sonra)
@csrf_exempt
def verify_linkedin(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    print("🚀 VERIFY LINKEDIN ENDPOINT ÇAĞRILDI!")
    
    user = get_user_from_jwt(request)
    if not user:
        print("❌ Kullanıcı bulunamadı")
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    print(f"✅ Kullanıcı bulundu: {user.email}")
    
    # Kimlik doğrulaması kontrol et
    if not getattr(user, 'identity_verified', False):
        return JsonResponse({
            'status': 'error', 
            'message': 'Önce kimlik doğrulaması yapmalısınız'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        linkedin_url = data.get('linkedin_url')
    except Exception as e:
        print(f"❌ JSON parse hatası: {e}")
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    if not linkedin_url:
        return JsonResponse({'status': 'error', 'message': 'LinkedIn URL gerekli'}, status=400)
    
    # LinkedIn profil analizi
    try:
        print(f"🔗 LINKEDIN ANALİZİ BAŞLATILIYOR...")
        print(f"🌐 LinkedIn URL: {linkedin_url}")
        
        linkedin_data = scrape_linkedin_profile(linkedin_url)
        
        print(f"📊 LinkedIn Analiz Sonucu: {linkedin_data}")
        
        if linkedin_data['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'LinkedIn analizi başarısız',
                'details': linkedin_data.get('message', 'Bilinmeyen hata')
            }, status=400)
        
        linkedin_name = linkedin_data.get('name')
        linkedin_summary = linkedin_data.get('summary', '')
        
        print(f"👤 LinkedIn'den çıkarılan: {linkedin_name}")
        
        # Kimlik-LinkedIn eşleşme kontrolü
        id_name = getattr(user, 'verified_name', '')
        id_surname = getattr(user, 'verified_surname', '')
        
        match_result = verify_identity_match(id_name, id_surname, linkedin_name)
        
        print(f"🔍 Eşleşme kontrolü: {match_result}")
        
        if match_result['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'Eşleşme kontrolü başarısız',
                'details': match_result.get('message', 'Bilinmeyen hata')
            }, status=400)
        
        if not match_result['match']:
            return JsonResponse({
                'status': 'error',
                'message': 'Kimlik adınız ile LinkedIn adınız eşleşmiyor',
                'id_name': f"{id_name} {id_surname}",
                'linkedin_name': linkedin_name
            }, status=400)
        
        # LinkedIn profil AI analizi
        profile_data = {
            'name': linkedin_name,
            'summary': linkedin_summary
        }
        
        ai_analysis = analyze_linkedin_profile(profile_data)
        
        if ai_analysis['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'LinkedIn AI analizi başarısız',
                'details': ai_analysis.get('message', 'Bilinmeyen hata')
            }, status=400)
        
        technical_analysis = ai_analysis.get('analysis', {})
        
        # Kullanıcı bilgilerini güncelle
        user.linkedin_url = linkedin_url
        user.linkedin_name = linkedin_name
        user.linkedin_verified = True
        
        user.languages_known = json.dumps(technical_analysis.get('skills', {}))
        user.experience_estimate = technical_analysis.get('experience_estimate', '')
        user.profile_summary = technical_analysis.get('summary', '')
        user.technical_analysis = json.dumps(technical_analysis)
        
        user.verification_status = 'verified'
        user.verification_notes = f"Tam doğrulama: Kimlik-LinkedIn eşleşmesi: {match_result['confidence']} güven"
        
        user.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'LinkedIn doğrulama başarılı',
            'verification': {
                'identity_verified': True,
                'linkedin_verified': True,
                'match_confidence': match_result['confidence'],
                'id_name': f"{id_name} {id_surname}",
                'linkedin_name': linkedin_name,
                'experience_estimate': technical_analysis.get('experience_estimate', ''),
                'skills_count': len(technical_analysis.get('skills', {}))
            }
        })
        
    except Exception as e:
        print(f"❌ LinkedIn analizi hatası: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'LinkedIn analizi hatası',
            'error': str(e)
        }, status=500)

# GET /api/auth/verification-status
# Açıklama: Kullanıcının doğrulama durumunu getirir
@csrf_exempt
def get_verification_status(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'GET olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız'}, status=401)
    
    return JsonResponse({
        'status': 'ok',
        'verification': {
            'identity_verified': getattr(user, 'identity_verified', False),
            'linkedin_verified': getattr(user, 'linkedin_verified', False),
            'verification_status': getattr(user, 'verification_status', 'pending'),
            'verified_name': getattr(user, 'verified_name', ''),
            'linkedin_name': getattr(user, 'linkedin_name', ''),
            'experience_estimate': getattr(user, 'experience_estimate', ''),
            'verification_notes': getattr(user, 'verification_notes', '')
        }
    })

# ADMIN ENDPOINT'LERİ

# GET /api/auth/admin/verification-requests
# Açıklama: Admin için tüm doğrulama isteklerini listeler
@csrf_exempt
def admin_verification_requests(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'GET olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user or 'admin' not in getattr(user, 'user_type', []):
        return JsonResponse({'status': 'error', 'message': 'Admin yetkisi gerekli'}, status=403)
    
    try:
        # Tüm doğrulama isteklerini getir
        pending_users = User.objects.filter(verification_status='pending')
        verified_users = User.objects.filter(verification_status='verified')
        rejected_users = User.objects.filter(verification_status='rejected')
        
        requests_data = []
        
        # Bekleyen istekler
        for user_obj in pending_users:
            requests_data.append({
                'user_id': str(user_obj.id),
                'email': user_obj.email,
                'full_name': user_obj.full_name,
                'verification_status': user_obj.verification_status,
                'identity_verified': getattr(user_obj, 'identity_verified', False),
                'linkedin_verified': getattr(user_obj, 'linkedin_verified', False),
                'verified_name': getattr(user_obj, 'verified_name', ''),
                'linkedin_name': getattr(user_obj, 'linkedin_name', ''),
                'experience_estimate': getattr(user_obj, 'experience_estimate', ''),
                'verification_notes': getattr(user_obj, 'verification_notes', ''),
                'created_at': user_obj.created_at.isoformat() if user_obj.created_at else None
            })
        
        return JsonResponse({
            'status': 'ok',
            'requests': requests_data,
            'counts': {
                'pending': len(pending_users),
                'verified': len(verified_users),
                'rejected': len(rejected_users)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Doğrulama istekleri getirilemedi',
            'error': str(e)
        }, status=500)

# POST /api/auth/admin/approve-verification
# Açıklama: Admin doğrulama isteğini onaylar
@csrf_exempt
def admin_approve_verification(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user or 'admin' not in getattr(user, 'user_type', []):
        return JsonResponse({'status': 'error', 'message': 'Admin yetkisi gerekli'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        admin_notes = data.get('admin_notes', '')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Kullanıcı ID gerekli'}, status=400)
    
    try:
        # Kullanıcıyı bul
        target_user = User.objects.get(id=user_id)
        
        # Doğrulama durumunu güncelle
        target_user.verification_status = 'verified'
        target_user.verification_notes = f"Admin onayı: {admin_notes}"
        target_user.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Doğrulama onaylandı',
            'user': {
                'id': str(target_user.id),
                'email': target_user.email,
                'full_name': target_user.full_name,
                'verification_status': target_user.verification_status
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Kullanıcı bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Doğrulama onaylanamadı',
            'error': str(e)
        }, status=500)

# POST /api/auth/admin/reject-verification
# Açıklama: Admin doğrulama isteğini reddeder
@csrf_exempt
def admin_reject_verification(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'}, status=405)
    
    user = get_user_from_jwt(request)
    if not user or 'admin' not in getattr(user, 'user_type', []):
        return JsonResponse({'status': 'error', 'message': 'Admin yetkisi gerekli'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        rejection_reason = data.get('rejection_reason', '')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Kullanıcı ID gerekli'}, status=400)
    
    try:
        # Kullanıcıyı bul
        target_user = User.objects.get(id=user_id)
        
        # Doğrulama durumunu güncelle
        target_user.verification_status = 'rejected'
        target_user.verification_notes = f"Admin reddi: {rejection_reason}"
        target_user.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Doğrulama reddedildi',
            'user': {
                'id': str(target_user.id),
                'email': target_user.email,
                'full_name': target_user.full_name,
                'verification_status': target_user.verification_status
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Kullanıcı bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Doğrulama reddedilemedi',
            'error': str(e)
        }, status=500)

@csrf_exempt  # Postman'dan test için CSRF'yi devre dışı bırakıyoruz
def verify_id_view(request):
    if request.method == 'POST':
        # JWT authentication
        user = get_user_from_token(request)
        if not user:
            return JsonResponse({'error': 'Geçersiz token veya kullanıcı bulunamadı.'}, status=401)
        
        if 'id_card_image' not in request.FILES:
            return JsonResponse({'error': 'Hiçbir dosya gelmedi.'}, status=400)
        img = request.FILES['id_card_image']
        if not img.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return JsonResponse({'error': 'Sadece kimlik fotoğrafı (.jpg, .jpeg, .png) yükleyin.'}, status=400)
        
        # Gemini'ye gönder ve cevabını döndür
        data = send_image_to_gemini(img)
        if not data:
            return JsonResponse({'error': 'Gemini cevap vermedi.'}, status=400)
        
        # Sadece Gemini'nin cevabını döndür
        return JsonResponse(data)
    return JsonResponse({'error': 'Sadece POST isteği desteklenir.'}, status=405)
