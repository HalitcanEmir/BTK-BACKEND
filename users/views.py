from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
import json
from .models import User, EmailVerification, PasswordReset
from .utils import hash_password, check_password, analyze_id_card, scrape_linkedin_profile, analyze_linkedin_profile, verify_identity_match, generate_verification_code, send_verification_email, send_welcome_email, send_password_reset_email
import jwt
from django.conf import settings
from .forms import IDCardForm, CVUploadForm
from .utils import send_image_to_gemini, extract_text_from_pdf, detect_name_from_cv, compare_names, analyze_cv_with_gemini
import base64
import os
from mongoengine.errors import DoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EmailVerification
from datetime import datetime, timedelta
import re
from .models import FriendRequest

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
# Açıklama: Yeni kullanıcı kaydı - Email doğrulama kodu gönderir
@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        user_type = data.get('user_type', [])
        github_token = data.get('github_token')
        linkedin_token = data.get('linkedin_token')
        card_token = data.get('card_token')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    
    # Validasyon
    if not email or not password or not full_name:
        return JsonResponse({'status': 'error', 'message': 'Email, şifre ve tam ad zorunludur'})
    
    if len(password) < 6:
        return JsonResponse({'status': 'error', 'message': 'Şifre en az 6 karakter olmalı'})
    
    # Email formatını kontrol et
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({'status': 'error', 'message': 'Geçersiz email formatı'})
    
    # Email zaten kayıtlı mı kontrol et
    existing_user = User.objects(email=email).first()
    if existing_user:
        return JsonResponse({'status': 'error', 'message': 'Bu email adresi zaten kayıtlı'})
    
    # Email doğrulama kodu oluştur ve gönder
    verification_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Veritabanına kaydet
    verification = EmailVerification(
        email=email,
        verification_code=verification_code,
        expires_at=expires_at
    )
    verification.save()
    
    # Email gönder
    email_sent = send_verification_email(email, verification_code)
    
    if not email_sent:
        # Email gönderilemezse veritabanından sil
        verification.delete()
        return JsonResponse({
            'status': 'error', 
            'message': 'Email gönderilemedi. Lütfen tekrar deneyin.'
        }, status=500)
    
    # Geçici kullanıcı bilgilerini döndür (henüz kayıt olmadı)
    temp_user_data = {
        'email': email,
        'full_name': full_name,
        'user_type': user_type,
        'message': 'Email doğrulama kodu gönderildi. Lütfen email\'inizi kontrol edin.'
    }
    
    return JsonResponse({
        'status': 'ok', 
        'message': 'Email doğrulama kodu gönderildi. Lütfen email\'inizi kontrol edin.',
        'user': temp_user_data,
        'requires_verification': True
    })

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
@csrf_exempt
def my_profile(request):
    """Kullanıcının kendi profilini görüntüleme"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Sadece GET isteği desteklenir.'}, status=405)
    
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Geçersiz token veya kullanıcı bulunamadı.'}, status=401)
    
    # Temel bilgiler
    data = {
        "id": str(user.id),
        "full_name": f"{user.verified_name or ''} {user.verified_surname or ''}".strip(),
        "email": user.email,
        "user_type": user.user_type,
        "identity_verified": user.identity_verified,
        "cv_verified": getattr(user, 'cv_verified', False),
        "github_verified": user.github_verified,
        "linkedin_verified": user.linkedin_verified,
        "can_invest": user.can_invest,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
    
    # CV'den gelen bilgiler
    if user.languages_known:
        try:
            data["languages"] = json.loads(user.languages_known)
        except:
            data["languages"] = []
    
    if user.known_languages:
        data["known_languages"] = user.known_languages
    
    if user.language_levels:
        try:
            data["language_levels"] = json.loads(user.language_levels)
        except:
            data["language_levels"] = {}
    
    # Kimlik bilgileri (sadece kendi profili için)
    if user.verified_name and user.verified_surname:
        data["verified_full_name"] = f"{user.verified_name} {user.verified_surname}"
    
    if user.tc_verified:
        data["tc_verified"] = True  # TC numarasını gösterme, sadece doğrulandığını belirt
    
    # CV dosyası
    if user.cv_file:
        data["cv_file"] = user.cv_file
    
    # Profil özeti
    if user.profile_summary:
        data["profile_summary"] = user.profile_summary
    
    # Teknik analiz
    if user.technical_analysis:
        try:
            data["technical_analysis"] = json.loads(user.technical_analysis)
        except:
            data["technical_analysis"] = {}
    
    return JsonResponse(data)

# Başka Kullanıcının Profili
# GET /api/users/<id>
# Açıklama: Başka bir kullanıcının profilini getirir
@csrf_exempt
def user_profile(request, user_id):
    """Başka bir kullanıcının profilini görüntüleme (kısıtlı bilgi)"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Sadece GET isteği desteklenir.'}, status=405)
    
    # Giriş yapmış kullanıcı kontrolü
    current_user = get_user_from_token(request)
    if not current_user:
        return JsonResponse({'error': 'Geçersiz token veya kullanıcı bulunamadı.'}, status=401)
    
    try:
        # Profili görüntülenecek kullanıcıyı bul
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Kullanıcı bulunamadı.'}, status=404)
    
    # Kısıtlı bilgiler (hassas bilgiler gizli)
    data = {
        "id": str(target_user.id),
        "full_name": f"{target_user.verified_name or ''} {target_user.verified_surname or ''}".strip(),
        "user_type": target_user.user_type,
        "identity_verified": target_user.identity_verified,
        "cv_verified": getattr(target_user, 'cv_verified', False),
        "github_verified": target_user.github_verified,
        "linkedin_verified": target_user.linkedin_verified,
        "can_invest": target_user.can_invest,
        "created_at": target_user.created_at.isoformat() if target_user.created_at else None,
    }
    
    # CV'den gelen bilgiler (kısıtlı)
    if target_user.known_languages:
        data["known_languages"] = target_user.known_languages
    
    if target_user.language_levels:
        try:
            data["language_levels"] = json.loads(target_user.language_levels)
        except:
            data["language_levels"] = {}
    
    # Profil özeti
    if target_user.profile_summary:
        data["profile_summary"] = target_user.profile_summary
    
    # Admin ise daha fazla bilgi göster
    if 'admin' in current_user.user_type:
        data["email"] = target_user.email
        if target_user.languages_known:
            try:
                data["languages"] = json.loads(target_user.languages_known)
            except:
                data["languages"] = []
    
    return JsonResponse(data)

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
        
        # Eğer ad, soyad ve tc varsa kullanıcıya kaydet
        name = data.get('name')
        surname = data.get('surname')
        tc = data.get('tc')
        if name and surname and tc:
            user.verified_name = name
            user.verified_surname = surname
            user.tc_verified = tc
            user.identity_verified = True
            user.save()
        
        # Sadece Gemini'nin cevabını döndür
        return JsonResponse(data)
    return JsonResponse({'error': 'Sadece POST isteği desteklenir.'}, status=405)

@csrf_exempt
def upload_cv_view(request):
    if request.method == 'POST':
        # JWT authentication
        user = get_user_from_token(request)
        if not user:
            return JsonResponse({'error': 'Geçersiz token veya kullanıcı bulunamadı.'}, status=401)
        
        # Debug: Kullanıcı durumunu kontrol et
        print(f"User ID: {user.id}")
        print(f"Identity verified: {user.identity_verified}")
        print(f"Verified name: {user.verified_name}")
        print(f"Verified surname: {user.verified_surname}")
        
        # Kimlik doğrulaması geçmiş mi kontrol et
        if not user.identity_verified or not user.verified_name or not user.verified_surname:
            return JsonResponse({
                'error': 'Önce kimlik doğrulaması yapmalısınız.',
                'debug': {
                    'identity_verified': user.identity_verified,
                    'verified_name': user.verified_name,
                    'verified_surname': user.verified_surname
                }
            }, status=400)
        
        form = CVUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return JsonResponse({'error': 'Geçersiz dosya formatı veya boyut.'}, status=400)
        
        cv_file = form.cleaned_data['cv_file']
        
        # CV'den metin çıkar
        cv_text = extract_text_from_pdf(cv_file)
        if not cv_text:
            return JsonResponse({'error': 'CV dosyasından metin çıkarılamadı.'}, status=400)
        
        # CV'den ad-soyad tespit et
        cv_name = detect_name_from_cv(cv_text)
        if not cv_name:
            return JsonResponse({'error': 'CV\'den ad-soyad tespit edilemedi.'}, status=400)
        
        # Kimlikteki ad-soyad ile karşılaştır
        id_full_name = f"{user.verified_name} {user.verified_surname}"
        
        if compare_names(cv_name, id_full_name):
            # Eşleşiyor - CV'yi kaydet ve analiz et
            user.cv_file = cv_file.name  # Dosya adını kaydet, dosya objesini değil
            user.cv_verified = True
            user.cv_name_detected = cv_name
            user.save()
            
            # CV'yi Gemini ile analiz et
            cv_analysis = analyze_cv_with_gemini(cv_text)
            
            if 'languages' in cv_analysis:
                # Programlama dillerini kullanıcıya kaydet
                user.languages_known = json.dumps(cv_analysis['languages'], ensure_ascii=False)
                
                # Dilleri ve seviyeleri ayrı ayrı kaydet
                if 'languages_list' in cv_analysis:
                    user.known_languages = cv_analysis['languages_list']
                
                if 'levels_summary' in cv_analysis:
                    user.language_levels = json.dumps(cv_analysis['levels_summary'], ensure_ascii=False)
                
                user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'CV başarıyla doğrulandı ve analiz edildi.',
                    'cv_name': cv_name,
                    'id_name': id_full_name,
                    'languages_analysis': cv_analysis['languages'],
                    'known_languages': cv_analysis.get('languages_list', []),
                    'language_levels': cv_analysis.get('levels_summary', {})
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'CV doğrulandı fakat dil analizi yapılamadı.',
                    'cv_name': cv_name,
                    'id_name': id_full_name,
                    'analysis_error': cv_analysis.get('error', 'Bilinmeyen hata')
                })
        else:
            # Eşleşmiyor
            return JsonResponse({
                'success': False,
                'error': 'CV\'deki ad-soyad kimlikle eşleşmiyor. Lütfen kendi CV\'nizi yükleyin.',
                'cv_name': cv_name,
                'id_name': id_full_name
            })
    
    return JsonResponse({'error': 'Sadece POST isteği desteklenir.'}, status=405)

@csrf_exempt
def send_verification_code(request):
    """Email doğrulama kodu gönderir"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    if not email:
        return JsonResponse({"status": "error", "message": "Email adresi gerekli"}, status=400)
    
    # Email formatını kontrol et
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({"status": "error", "message": "Geçersiz email formatı"}, status=400)
    
    # Email zaten kayıtlı mı kontrol et - KALDIRILDI
    # existing_user = User.objects(email=email).first()
    # if existing_user:
    #     return JsonResponse({"status": "error", "message": "Bu email adresi zaten kayıtlı"}, status=400)
    
    # Eski doğrulama kodlarını temizle - KALDIRILDI
    # EmailVerification.objects(email=email, is_used=False).delete()
    
    # Yeni doğrulama kodu oluştur
    verification_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Veritabanına kaydet
    verification = EmailVerification(
        email=email,
        verification_code=verification_code,
        expires_at=expires_at
    )
    verification.save()
    
    # Email gönder
    email_sent = send_verification_email(email, verification_code)
    
    if email_sent:
        return JsonResponse({
            "status": "ok",
            "message": "Doğrulama kodu email adresinize gönderildi. Lütfen email'inizi kontrol edin.",
            "email": email
        })
    else:
        # Email gönderilemezse veritabanından sil
        verification.delete()
        return JsonResponse({
            "status": "error",
            "message": "Email gönderilemedi. Lütfen tekrar deneyin."
        }, status=500)

@csrf_exempt
def verify_email_and_register(request):
    """Email doğrulama ve kayıt işlemi"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        verification_code = data.get('verification_code', '').strip()
        full_name = data.get('full_name', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', [])
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    # Validasyon
    if not all([email, verification_code, full_name, password]):
        return JsonResponse({"status": "error", "message": "Tüm alanlar gerekli"}, status=400)
    
    if len(password) < 6:
        return JsonResponse({"status": "error", "message": "Şifre en az 6 karakter olmalı"}, status=400)
    
    # Doğrulama kodunu kontrol et
    verification = EmailVerification.objects(
        email=email,
        verification_code=verification_code,
        is_used=False,
        expires_at__gt=datetime.utcnow()
    ).first()
    
    if not verification:
        return JsonResponse({"status": "error", "message": "Geçersiz veya süresi dolmuş doğrulama kodu"}, status=400)
    
    # Email zaten kayıtlı mı kontrol et
    existing_user = User.objects(email=email).first()
    if existing_user:
        return JsonResponse({"status": "error", "message": "Bu email adresi zaten kayıtlı"}, status=400)
    
    try:
        # Kullanıcıyı oluştur
        hashed_password = hash_password(password)
        user = User(
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            user_type=user_type if user_type else ['developer'],
            created_at=datetime.utcnow()
        )
        user.save()
        
        # Doğrulama kodunu kullanıldı olarak işaretle
        verification.is_used = True
        verification.save()
        
        # Hoş geldin email'i gönder
        send_welcome_email(email, full_name)
        
        # JWT token oluştur
        token = jwt.encode(
            {
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return JsonResponse({
            "status": "ok",
            "message": "Kayıt başarılı! Hoş geldiniz.",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "user_type": user.user_type
            },
            "token": token
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "Kayıt sırasında hata oluştu",
            "error": str(e)
        }, status=500)

@csrf_exempt
def resend_verification_code(request):
    """Doğrulama kodunu tekrar gönderir"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    if not email:
        return JsonResponse({"status": "error", "message": "Email adresi gerekli"}, status=400)
    
    # Kullanıcı zaten kayıtlı mı kontrol et - KALDIRILDI
    # existing_user = User.objects(email=email).first()
    # if existing_user:
    #     return JsonResponse({"status": "error", "message": "Bu email adresi zaten kayıtlı"}, status=400)
    
    # Eski doğrulama kodlarını temizle - KALDIRILDI
    # EmailVerification.objects(email=email, is_used=False).delete()
    
    # Yeni kod oluştur
    verification_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    verification = EmailVerification(
        email=email,
        verification_code=verification_code,
        expires_at=expires_at
    )
    verification.save()
    
    # Email gönder
    email_sent = send_verification_email(email, verification_code)
    
    if email_sent:
        return JsonResponse({
            "status": "ok",
            "message": "Yeni doğrulama kodu gönderildi. Lütfen email'inizi kontrol edin.",
            "email": email
        })
    else:
        verification.delete()
        return JsonResponse({
            "status": "error",
            "message": "Email gönderilemedi. Lütfen tekrar deneyin."
        }, status=500)

@csrf_exempt
def send_password_reset_code(request):
    """Şifre sıfırlama kodu gönderir"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    if not email:
        return JsonResponse({"status": "error", "message": "Email adresi gerekli"}, status=400)
    
    # Email formatını kontrol et
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({"status": "error", "message": "Geçersiz email formatı"}, status=400)
    
    # Kullanıcı var mı kontrol et
    user = User.objects(email=email).first()
    if not user:
        return JsonResponse({"status": "error", "message": "Bu email adresi ile kayıtlı kullanıcı bulunamadı"}, status=400)
    
    # Yeni sıfırlama kodu oluştur
    reset_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Veritabanına kaydet
    password_reset = PasswordReset(
        email=email,
        reset_code=reset_code,
        expires_at=expires_at
    )
    password_reset.save()
    
    # Email gönder
    email_sent = send_password_reset_email(email, reset_code)
    
    if email_sent:
        return JsonResponse({
            "status": "ok",
            "message": "Şifre sıfırlama kodu email adresinize gönderildi. Lütfen email'inizi kontrol edin.",
            "email": email
        })
    else:
        # Email gönderilemezse veritabanından sil
        password_reset.delete()
        return JsonResponse({
            "status": "error",
            "message": "Email gönderilemedi. Lütfen tekrar deneyin."
        }, status=500)

@csrf_exempt
def verify_reset_code_and_change_password(request):
    """Sıfırlama kodunu doğrular ve şifreyi değiştirir"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        reset_code = data.get('reset_code', '').strip()
        new_password = data.get('new_password', '')
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    # Validasyon
    if not all([email, reset_code, new_password]):
        return JsonResponse({"status": "error", "message": "Tüm alanlar gerekli"}, status=400)
    
    if len(new_password) < 6:
        return JsonResponse({"status": "error", "message": "Şifre en az 6 karakter olmalı"}, status=400)
    
    # Sıfırlama kodunu kontrol et
    password_reset = PasswordReset.objects(
        email=email,
        reset_code=reset_code,
        is_used=False,
        expires_at__gt=datetime.utcnow()
    ).first()
    
    if not password_reset:
        return JsonResponse({"status": "error", "message": "Geçersiz veya süresi dolmuş sıfırlama kodu"}, status=400)
    
    # Kullanıcıyı bul
    user = User.objects(email=email).first()
    if not user:
        return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı"}, status=400)
    
    try:
        # Şifreyi güncelle
        hashed_password = hash_password(new_password)
        user.password_hash = hashed_password
        user.save()
        
        # Sıfırlama kodunu kullanıldı olarak işaretle
        password_reset.is_used = True
        password_reset.save()
        
        return JsonResponse({
            "status": "ok",
            "message": "Şifreniz başarıyla güncellendi!",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "Şifre güncellenirken hata oluştu",
            "error": str(e)
        }, status=500)

@csrf_exempt
def resend_password_reset_code(request):
    """Şifre sıfırlama kodunu tekrar gönderir"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except Exception:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON"}, status=400)
    
    if not email:
        return JsonResponse({"status": "error", "message": "Email adresi gerekli"}, status=400)
    
    # Kullanıcı var mı kontrol et
    user = User.objects(email=email).first()
    if not user:
        return JsonResponse({"status": "error", "message": "Bu email adresi ile kayıtlı kullanıcı bulunamadı"}, status=400)
    
    # Yeni kod oluştur
    reset_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    password_reset = PasswordReset(
        email=email,
        reset_code=reset_code,
        expires_at=expires_at
    )
    password_reset.save()
    
    # Email gönder
    email_sent = send_password_reset_email(email, reset_code)
    
    if email_sent:
        return JsonResponse({
            "status": "ok",
            "message": "Yeni şifre sıfırlama kodu gönderildi. Lütfen email'inizi kontrol edin.",
            "email": email
        })
    else:
        password_reset.delete()
        return JsonResponse({
            "status": "error",
            "message": "Email gönderilemedi. Lütfen tekrar deneyin."
        }, status=500)

@csrf_exempt
def update_profile(request):
    """Kullanıcı profilini günceller"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Geçersiz token"}, status=401)
    
    try:
        data = json.loads(request.body)
        
        # Güncellenebilir alanlar
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        
        if 'bio' in data:
            user.bio = data['bio'].strip()
        
        if 'location' in data:
            user.location = data['location'].strip()
        
        if 'website' in data:
            user.website = data['website'].strip()
        
        if 'phone' in data:
            user.phone = data['phone'].strip()
        
        if 'github_username' in data:
            user.github_username = data['github_username'].strip()
        
        if 'linkedin_username' in data:
            user.linkedin_username = data['linkedin_username'].strip()
        
        if 'twitter_username' in data:
            user.twitter_username = data['twitter_username'].strip()
        
        user.updated_at = datetime.utcnow()
        user.save()
        
        return JsonResponse({
            "status": "ok",
            "message": "Profil başarıyla güncellendi",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "bio": user.bio,
                "location": user.location,
                "website": user.website,
                "phone": user.phone,
                "github_username": user.github_username,
                "linkedin_username": user.linkedin_username,
                "twitter_username": user.twitter_username,
                "avatar": user.avatar
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "Profil güncellenirken hata oluştu",
            "error": str(e)
        }, status=500)

@csrf_exempt
def upload_avatar(request):
    """Avatar yükler"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Geçersiz token"}, status=401)
    
    try:
        if 'avatar' not in request.FILES:
            return JsonResponse({"status": "error", "message": "Avatar dosyası gerekli"}, status=400)
        
        avatar_file = request.FILES['avatar']
        
        # Dosya boyutu kontrolü (5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({"status": "error", "message": "Dosya boyutu 5MB'dan küçük olmalı"}, status=400)
        
        # Dosya tipi kontrolü
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({"status": "error", "message": "Sadece JPEG, PNG ve GIF dosyaları kabul edilir"}, status=400)
        
        # Dosya adını oluştur
        import uuid
        file_extension = avatar_file.name.split('.')[-1]
        filename = f"avatar_{user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Dosyayı kaydet (gerçek uygulamada cloud storage kullanılır)
        import os
        upload_dir = 'uploads/avatars/'
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in avatar_file.chunks():
                destination.write(chunk)
        
        # Avatar URL'ini güncelle
        avatar_url = f"/media/avatars/{filename}"
        user.avatar = avatar_url
        user.updated_at = datetime.utcnow()
        user.save()
        
        return JsonResponse({
            "status": "ok",
            "message": "Avatar başarıyla yüklendi",
            "avatar_url": avatar_url
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "Avatar yüklenirken hata oluştu",
            "error": str(e)
        }, status=500)

@csrf_exempt
def delete_account(request):
    """Kullanıcı hesabını siler"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"status": "error", "message": "Geçersiz token"}, status=401)
    
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
        
        # Şifre doğrulama
        if not check_password(password, user.password_hash):
            return JsonResponse({"status": "error", "message": "Şifre yanlış"}, status=400)
        
        # Hesabı sil (soft delete)
        user.is_active = False
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        user.save()
        
        return JsonResponse({
            "status": "ok",
            "message": "Hesabınız başarıyla silindi"
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "Hesap silinirken hata oluştu",
            "error": str(e)
        }, status=500)

@csrf_exempt
def test_email_settings(request):
    """Email ayarlarını test eder"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST olmalı"}, status=405)
    
    try:
        data = json.loads(request.body)
        test_email = data.get('email', 'test@example.com')
    except Exception:
        test_email = 'test@example.com'
    
    from .utils import test_email_configuration, get_email_settings_info
    
    # Ayarları göster
    settings_info = get_email_settings_info()
    
    # Test et
    test_result = test_email_configuration()
    
    if test_result:
        return JsonResponse({
            "status": "ok",
            "message": "Email ayarları başarılı!",
            "settings": settings_info,
            "test_email": test_email
        })
    else:
        return JsonResponse({
            "status": "error",
            "message": "Email ayarlarında hata var!",
            "settings": settings_info,
            "test_email": test_email
        }, status=500)
