from django.db import models
from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, IntField, FloatField
import datetime

# Create your models here.

class User(Document):
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    full_name = StringField(required=True)
    user_type = ListField(StringField())  # ['developer', 'investor', 'admin']
    github_verified = BooleanField(default=False)
    linkedin_verified = BooleanField(default=False)
    can_invest = BooleanField(default=False)
    created_at = DateTimeField()
    
    # Kimlik doğrulama alanları
    id_card_image_url = StringField()  # Kimlik görseli URL'si
    verified_name = StringField()  # Kimlikten çıkarılan ad
    verified_surname = StringField()  # Kimlikten çıkarılan soyad
    identity_verified = BooleanField(default=False)  # Kimlik doğrulandı mı?
    
    # LinkedIn alanları
    linkedin_url = StringField()  # LinkedIn profil URL'si
    linkedin_name = StringField()  # LinkedIn'den çıkarılan ad
    linkedin_verified = BooleanField(default=False)  # LinkedIn doğrulandı mı?
    
    # AI analiz sonuçları
    languages_known = StringField()  # JSON string olarak beceriler
    experience_estimate = StringField()  # Tahmini deneyim süresi
    profile_summary = StringField()  # AI özeti
    technical_analysis = StringField()  # Teknik analiz JSON
    
    # Doğrulama durumu
    verification_status = StringField(default='pending', choices=['pending', 'id_verified', 'verified', 'rejected'])
    verification_notes = StringField()  # Doğrulama notları
    tc_verified = StringField()  # Kimlikten doğrulanan T.C. Kimlik No
    
    # CV doğrulama alanları
    cv_file = StringField()  # CV dosyası URL'si
    cv_verified = BooleanField(default=False)  # CV doğrulandı mı?
    cv_name_detected = StringField()  # CV'den tespit edilen ad-soyad
    
    # Programlama dilleri ve seviyeleri
    known_languages = ListField(StringField())  # Bilinen diller listesi
    language_levels = StringField()  # Dillerin seviyeleri JSON string
    
    # Performans skoru alanları
    reliability_score = IntField(default=100)  # Güven skoru (0-1000)
    total_tasks = IntField(default=0)  # Toplam görev sayısı
    completed_tasks = IntField(default=0)  # Tamamlanan görev sayısı
    overdue_tasks = IntField(default=0)  # Geciken görev sayısı
    on_time_tasks = IntField(default=0)  # Zamanında tamamlanan görev sayısı
    average_completion_time = FloatField(default=0.0)  # Ortalama tamamlanma süresi (gün)
    last_performance_update = DateTimeField()  # Son performans güncelleme tarihi
