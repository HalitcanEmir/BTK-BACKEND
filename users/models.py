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
