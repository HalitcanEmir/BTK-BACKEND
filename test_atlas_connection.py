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
        
        # Atlas connection string - Mevcut btkdb database'ini kullan
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
            username="test_atlas_user",
            email="test@atlas.com",
            first_name="Test",
            last_name="Atlas"
        )
        test_user.save()
        print("✅ Test kullanıcısı oluşturuldu")
        
        # Kullanıcıyı bul
        found_user = User.objects(username="test_atlas_user").first()
        if found_user:
            print(f"✅ Kullanıcı bulundu: {found_user.username}")
            # Test kullanıcısını sil
            found_user.delete()
            print("✅ Test kullanıcısı silindi")
        
        print("\n🎉 Tüm testler başarılı! Atlas bağlantısı çalışıyor.")
        return True
        
    except Exception as e:
        print(f"❌ Atlas bağlantı hatası: {e}")
        return False

if __name__ == "__main__":
    success = test_atlas_connection()
    sys.exit(0 if success else 1) 