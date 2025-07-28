from django.db import models
from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, IntField, FloatField, ReferenceField
import datetime

# Create your models here.

class User(Document):
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    full_name = StringField(required=True)
    user_type = ListField(StringField(), default=['developer'])
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    # Profil bilgileri
    avatar = StringField()  # Avatar URL'i
    bio = StringField(max_length=500)  # Kullanıcı hakkında
    location = StringField()  # Konum
    website = StringField()  # Kişisel website
    phone = StringField()  # Telefon numarası
    
    # Sosyal medya
    github_username = StringField()
    linkedin_username = StringField()
    twitter_username = StringField()
    
    # Arkadaşlık sistemi
    friends = ListField(ReferenceField('User'), default=[])  # Arkadaşlar
    friend_requests = ListField(ReferenceField('User'), default=[])  # Gelen arkadaşlık istekleri
    sent_friend_requests = ListField(ReferenceField('User'), default=[])  # Gönderilen arkadaşlık istekleri
    
    # Doğrulama alanları
    identity_verified = BooleanField(default=False)
    verified_name = StringField()
    verified_surname = StringField()
    github_verified = BooleanField(default=False)
    linkedin_verified = BooleanField(default=False)
    can_invest = BooleanField(default=False)
    
    # Performans skoru alanları
    reliability_score = IntField(default=100)  # Güven skoru (0-1000)
    total_tasks = IntField(default=0)  # Toplam görev sayısı
    completed_tasks = IntField(default=0)  # Tamamlanan görev sayısı
    overdue_tasks = IntField(default=0)  # Geciken görev sayısı
    on_time_tasks = IntField(default=0)  # Zamanında tamamlanan görev sayısı
    average_completion_time = FloatField(default=0.0)  # Ortalama tamamlanma süresi (gün)
    last_performance_update = DateTimeField()  # Son performans güncelleme tarihi
    
    # Hesap durumu
    is_active = BooleanField(default=True)  # Hesap aktif mi
    is_deleted = BooleanField(default=False)  # Hesap silinmiş mi
    deleted_at = DateTimeField()  # Silinme tarihi
    
    meta = {
        'indexes': [
            {'fields': ['email']},
            {'fields': ['user_type']},
            {'fields': ['identity_verified']},
            {'fields': ['reliability_score']},
            {'fields': ['is_active']},
            {'fields': ['is_deleted']}
        ]
    }

class FriendRequest(Document):
    """Arkadaşlık istekleri"""
    from_user = ReferenceField('User', required=True)
    to_user = ReferenceField('User', required=True)
    status = StringField(choices=['pending', 'accepted', 'rejected'], default='pending')
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'indexes': [
            {'fields': ['from_user', 'to_user'], 'unique': True},
            {'fields': ['to_user', 'status']},
            {'fields': ['status']}
        ]
    }

class EmailVerification(Document):
    """Email doğrulama kodları"""
    email = StringField(required=True)
    verification_code = StringField(required=True, max_length=6)
    is_used = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    expires_at = DateTimeField(required=True)
    
    meta = {
        'indexes': [
            {'fields': ['email', 'verification_code']},
            {'fields': ['email', 'is_used']},
            {'fields': ['expires_at']}
        ]
    }

class PasswordReset(Document):
    """Şifre sıfırlama kodları"""
    email = StringField(required=True)
    reset_code = StringField(required=True, max_length=6)
    is_used = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    expires_at = DateTimeField(required=True)
    
    meta = {
        'indexes': [
            {'fields': ['email', 'reset_code']},
            {'fields': ['email', 'is_used']},
            {'fields': ['expires_at']}
        ]
    }
