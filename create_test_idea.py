#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ideas.models import Idea
from users.models import User

def create_test_idea():
    """Test için onaylanmış fikir oluştur"""
    
    # Önce bir kullanıcı bul veya oluştur
    user = User.objects.first()
    if not user:
        print("Kullanıcı bulunamadı. Önce bir kullanıcı oluşturun.")
        return
    
    # Test fikri oluştur
    idea = Idea(
        title="Mobil Uygulama Geliştirme Platformu",
        description="Geliştiricilerin mobil uygulama geliştirmesini kolaylaştıran bir platform. Drag-and-drop arayüzü ile kod yazmadan uygulama oluşturabilirsiniz.",
        category="technology",
        problem="Mobil uygulama geliştirmek için programlama bilgisi gerekiyor",
        solution="Görsel arayüz ile kod yazmadan uygulama oluşturma",
        estimated_cost=50000.0,
        owner_id=user,
        created_by=user,
        approved_by=user,
        license_accepted=True,
        license_accepted_at=datetime.utcnow(),
        owner_share_percent=10,
        status='approved',  # Direkt onaylanmış
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        approved_at=datetime.utcnow(),
        likes=5,
        dislikes=1,
        passes=2,
        swipe_score=0.8
    )
    idea.save()
    
    print(f"Test fikri oluşturuldu: {idea.title}")
    print(f"ID: {idea.id}")
    print(f"Status: {idea.status}")
    
    # İkinci test fikri
    idea2 = Idea(
        title="Sürdürülebilir Enerji Çözümleri",
        description="Güneş ve rüzgar enerjisi ile ev ve işyerlerinin enerji ihtiyacını karşılayan sistemler.",
        category="environment",
        problem="Fosil yakıtlar çevre kirliliğine neden oluyor",
        solution="Yenilenebilir enerji sistemleri",
        estimated_cost=75000.0,
        owner_id=user,
        created_by=user,
        approved_by=user,
        license_accepted=True,
        license_accepted_at=datetime.utcnow(),
        owner_share_percent=15,
        status='approved',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        approved_at=datetime.utcnow(),
        likes=8,
        dislikes=0,
        passes=1,
        swipe_score=0.9
    )
    idea2.save()
    
    print(f"İkinci test fikri oluşturuldu: {idea2.title}")
    print(f"ID: {idea2.id}")
    print(f"Status: {idea2.status}")

if __name__ == "__main__":
    create_test_idea() 