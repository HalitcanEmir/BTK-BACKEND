from django.db import models
from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, IntField, FloatField, ReferenceField
import datetime

# Create your models here.

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
