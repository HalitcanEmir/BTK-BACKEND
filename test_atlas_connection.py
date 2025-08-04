#!/usr/bin/env python
"""
MongoDB Atlas bağlantı testi
Bu script Atlas bağlantısını test eder ve database işlemlerini kontrol eder
"""

import os
import sys
import django

# Django settings'i yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from mongoengine import connect, disconnect
from users.models import User

def test_atlas_connection():
    """Atlas bağlantısını test eder"""
    try:
        # Önce mevcut bağlantıyı kapat
        disconnect()
        
        # Atlas connection string - Güncellenmiş connection string
        atlas_connection_string = "mongodb+srv://halitcanemir06:1591235He@cluster0.eqsstlg.mongodb.net/btkdb?retryWrites=true&w=majority&appName=Cluster0"
        
        print("🔗 MongoDB Atlas'a bağlanıyor...")
        connect(host=atlas_connection_string, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
        print("✅ Atlas bağlantısı başarılı!")
        
        # Database işlemlerini test et
        print("\n📊 Database işlemleri test ediliyor...")
        
        # Kullanıcı sayısını kontrol et
        user_count = User.objects.count()
        print(f"👥 Toplam kullanıcı sayısı: {user_count}")
        
        # Test kullanıcısı oluştur
        test_user = User(
            email="test@atlas.com",
            full_name="Test Atlas User",
            password_hash="test_hash_123",
            user_type=["developer"]
        )
        test_user.save()
        print("✅ Test kullanıcısı oluşturuldu")
        
        # Kullanıcıyı bul
        found_user = User.objects(email="test@atlas.com").first()
        if found_user:
            print(f"✅ Kullanıcı bulundu: {found_user.full_name}")
            # Test kullanıcısını sil
            found_user.delete()
            print("✅ Test kullanıcısı silindi")
        
        print("\n🎉 Tüm testler başarılı! Atlas bağlantısı çalışıyor.")
        return True
        
    except Exception as e:
        print(f"❌ Atlas bağlantı hatası: {e}")
        return False

def list_all_users():
    """Veritabanındaki tüm kullanıcıları listeler"""
    try:
        print("\n📋 Veritabanındaki kullanıcılar:")
        print("=" * 50)
        
        users = User.objects.all()
        
        if not users:
            print("❌ Hiç kullanıcı bulunamadı")
            return
        
        for i, user in enumerate(users, 1):
            print(f"\n👤 Kullanıcı {i}:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Ad Soyad: {user.full_name}")
            print(f"   Roller: {user.user_type}")
            print(f"   GitHub Doğrulama: {'✅' if user.github_verified else '❌'}")
            print(f"   LinkedIn Doğrulama: {'✅' if user.linkedin_verified else '❌'}")
            print(f"   Yatırım Yapabilir: {'✅' if user.can_invest else '❌'}")
            print(f"   Kayıt Tarihi: {user.created_at}")
            print("-" * 30)
        
        print(f"\n🎯 Toplam {len(users)} kullanıcı bulundu!")
        
    except Exception as e:
        print(f"❌ Kullanıcı listesi alınırken hata: {e}")

if __name__ == "__main__":
    success = test_atlas_connection()
    if success:
        list_all_users()
    sys.exit(0 if success else 1) 