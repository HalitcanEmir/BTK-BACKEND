from django.shortcuts import render
from django.http import JsonResponse
from .models import Person
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .utils import create_magiclink_token, verify_magiclink_token
from .models import User
import json

# Create your views here.

# Yeni bir kişi ekler
# Örnek: /add/?name=Ali&age=30
# Response örneği: {"status": "ok", "id": "..."}
def add_person(request):
    # Query parametrelerinden isim ve yaş alınır
    name = request.GET.get('name')
    age = request.GET.get('age')
    if name and age:
        # Kişi kaydı oluşturulur ve MongoDB'ye kaydedilir
        person = Person(name=name, age=int(age))
        person.save()
        return JsonResponse({'status': 'ok', 'id': str(person.id)})
    # Eksik parametre varsa hata döner
    return JsonResponse({'status': 'error', 'message': 'name and age required'})

# Tüm kişileri listeler
# Örnek: /list/
# Response örneği: {"people": [{"id": "...", "name": "Ali", "age": 30}, ...]}
def list_people(request):
    # MongoDB'den tüm kişi kayıtları çekilir
    people = Person.objects.all()
    data = [{'id': str(p.id), 'name': p.name, 'age': p.age} for p in people]
    return JsonResponse({'people': data})

@csrf_exempt
# Kullanıcı e-posta ile giriş ister, magic link gönderilir
# POST /api/auth/request-login
# Body: {"email": "kullanici@site.com"}
# Response örneği: {"status": "ok"}
def request_login(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST olmalı'})
    try:
        data = json.loads(request.body)
        email = data.get('email')
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'})
    if not email:
        return JsonResponse({'status': 'error', 'message': 'E-posta zorunlu'})
    # Kullanıcıyı bul veya oluştur
    user = User.objects(email=email).first()
    if not user:
        user = User(email=email)
        user.save()
    # Magic link token üret
    token = create_magiclink_token(email)
    magic_link = f"http://localhost:8000/api/auth/verify-login?token={token}"
    # Gerçek projede e-posta gönderimi yapılmalı, burada konsola yazıyoruz
    print(f"Magic link: {magic_link}")
    return JsonResponse({'status': 'ok'})

# Magic link ile giriş yapılır
# GET /api/auth/verify-login?token=...
# Response örneği: {"status": "ok", "jwt": "...", "user": {...}}
def verify_login(request):
    token = request.GET.get('token')
    if not token:
        return JsonResponse({'status': 'error', 'message': 'Token zorunlu'})
    email = verify_magiclink_token(token)
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Token geçersiz veya süresi dolmuş'})
    user = User.objects(email=email).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Kullanıcı bulunamadı'})
    # Son giriş zamanını güncelle
    user.last_login = timezone.now()
    user.save()
    # Kullanıcıya oturum JWT'si üret (örnek, magic link token tekrar kullanılabilir)
    session_token = create_magiclink_token(email)
    user_data = {
        'email': user.email,
        'full_name': user.full_name,
        'is_developer': user.is_developer,
        'is_investor': user.is_investor,
        'linkedin_connected': user.linkedin_connected,
        'github_connected': user.github_connected,
        'card_verified': user.card_verified,
        'created_at': str(user.created_at),
        'last_login': str(user.last_login)
    }
    return JsonResponse({'status': 'ok', 'jwt': session_token, 'user': user_data})
