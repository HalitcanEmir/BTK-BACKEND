from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# Giriş Yap
# POST /api/auth/login
# Açıklama: Kullanıcı giriş endpointi (magic link veya şifreli)
def login(request):
    return JsonResponse({"message": "Giriş Yap"})

# Kayıt Ol
# POST /api/auth/register
# Açıklama: Yeni kullanıcı kaydı
def register(request):
    return JsonResponse({"message": "Kayıt Ol"})

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
