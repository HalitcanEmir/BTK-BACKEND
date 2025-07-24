from django.db import models
from mongoengine import Document, StringField, BooleanField, DateTimeField
import datetime

# Person: MongoDB'de saklanacak kişi bilgisi modeli
class Person(Document):
    name = StringField(required=True, max_length=100)  # Kişinin adı
    age = IntField(required=True)  # Kişinin yaşı

# User: Platform kullanıcısı modeli
class User(Document):
    email = StringField(required=True, unique=True)  # Kullanıcı e-posta adresi
    full_name = StringField()  # Kullanıcının tam adı
    is_developer = BooleanField(default=False)  # Geliştirici rolü
    is_investor = BooleanField(default=False)  # Yatırımcı rolü
    linkedin_connected = BooleanField(default=False)  # LinkedIn bağlantı durumu
    github_connected = BooleanField(default=False)  # GitHub bağlantı durumu
    card_verified = BooleanField(default=False)  # Kart doğrulama durumu
    created_at = DateTimeField(default=datetime.datetime.utcnow)  # Oluşturulma zamanı
    last_login = DateTimeField()  # Son giriş zamanı
