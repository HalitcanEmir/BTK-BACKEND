from django.db import models
from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, IntField, FloatField, ReferenceField
import datetime

# Create your models here.

class User(Document):
    email = StringField(required=True, unique=True)  # Kullanıcı e-posta adresi
    password_hash = StringField(required=True)  # Hashlenmiş şifre
    full_name = StringField()  # Kullanıcının tam adı
    user_type = ListField(StringField(choices=["developer", "entrepreneur", "investor", "fikir_sahibi", "admin"]))  # Kullanıcı rolleri (admin eklendi)
    github_verified = BooleanField(default=False)  # GitHub doğrulama durumu
    linkedin_verified = BooleanField(default=False)  # LinkedIn doğrulama durumu
    can_invest = BooleanField(default=False)  # Yatırım yapabilir mi?
    created_at = DateTimeField(default=datetime.datetime.utcnow)  # Kayıt tarihi
    reset_token = StringField()  # Şifre sıfırlama token'ı
    reset_token_expiry = DateTimeField()  # Token'ın geçerlilik süresi
    
    # Kimlik doğrulama alanları
    identity_verified = BooleanField(default=False)  # Kimlik doğrulandı mı?
    verified_name = StringField()  # Kimlikten çıkarılan ad
    verified_surname = StringField()  # Kimlikten çıkarılan soyad
    tc_verified = StringField()  # TC kimlik numarası
    id_card_image_url = StringField()  # Kimlik kartı resmi URL'i
    
    # CV alanları
    cv_verified = BooleanField(default=False)  # CV doğrulandı mı?
    cv_file = StringField()  # CV dosya adı
    cv_name_detected = StringField()  # CV'den çıkarılan ad
    languages_known = StringField()  # JSON formatında programlama dilleri
    known_languages = ListField(StringField())  # Programlama dilleri listesi
    language_levels = StringField()  # JSON formatında dil seviyeleri
    profile_summary = StringField()  # Profil özeti
    technical_analysis = StringField()  # Teknik analiz

class EmailVerification(Document):
    email = StringField(required=True)
    verification_code = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    expires_at = DateTimeField(required=True)
    is_used = BooleanField(default=False)

class PasswordReset(Document):
    email = StringField(required=True)
    reset_code = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    expires_at = DateTimeField(required=True)
    is_used = BooleanField(default=False)

class FriendRequest(Document):
    from_user = ReferenceField(User, required=True)
    to_user = ReferenceField(User, required=True)
    status = StringField(choices=["pending", "accepted", "rejected"], default="pending")
    created_at = DateTimeField(default=datetime.datetime.utcnow)
