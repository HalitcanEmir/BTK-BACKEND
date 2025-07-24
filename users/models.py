from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField
import datetime

# Kullanıcı modeli
class User(Document):
    email = StringField(required=True, unique=True)  # Kullanıcı e-posta adresi
    password_hash = StringField(required=True)  # Hashlenmiş şifre
    full_name = StringField()  # Kullanıcının tam adı
    user_type = ListField(StringField(choices=["developer", "entrepreneur", "investor"]))  # Kullanıcı rolleri
    github_verified = BooleanField(default=False)  # GitHub doğrulama durumu
    linkedin_verified = BooleanField(default=False)  # LinkedIn doğrulama durumu
    can_invest = BooleanField(default=False)  # Yatırım yapabilir mi?
    created_at = DateTimeField(default=datetime.datetime.utcnow)  # Kayıt tarihi
