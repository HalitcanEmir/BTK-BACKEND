#!/usr/bin/env python3
"""
Gemini AI Görev Planlaması Test Senaryosu

Bu dosya, Gemini AI ile görev planlaması sisteminin nasıl çalıştığını gösterir.
"""

import json
from datetime import datetime

def test_gemini_task_planning():
    """Gemini AI görev planlaması test senaryosu"""
    
    print("=== Gemini AI Görev Planlaması Test Senaryosu ===\n")
    
    # Test verisi
    test_data = {
        "project_name": "E-Ticaret Platformu",
        "project_description": "Modern e-ticaret platformu geliştirme projesi",
        "project_needs": "Üye girişi, ürün kataloğu, sepet sistemi, ödeme entegrasyonu, admin paneli",
        "team_members": [
            {
                "name": "Halitcan",
                "role": "backend",
                "available_hours": 4,
                "skills": ["Python", "Django", "PostgreSQL", "REST API"]
            },
            {
                "name": "Ayşe",
                "role": "frontend",
                "available_hours": 6,
                "skills": ["React", "TypeScript", "HTML", "CSS", "JavaScript"]
            },
            {
                "name": "Mehmet",
                "role": "test",
                "available_hours": 3,
                "skills": ["Selenium", "Jest", "Manual Testing"]
            }
        ]
    }
    
    print("1. Gemini'ye Gönderilecek Veri")
    print("-" * 40)
    print(f"Proje: {test_data['project_name']}")
    print(f"Açıklama: {test_data['project_description']}")
    print(f"İhtiyaçlar: {test_data['project_needs']}")
    print("\nEkip Üyeleri:")
    for member in test_data['team_members']:
        print(f"- {member['name']}: {member['role']} rolü, {member['available_hours']} saat/gün")
        print(f"  Yetenekler: {', '.join(member['skills'])}")
    
    print("\n2. Gemini'ye Gönderilecek Prompt")
    print("-" * 40)
    
    prompt = f"""
    Sen bir proje yöneticisisin. Aşağıdaki proje ve ekip bilgilerine göre detaylı görev planlaması yap.

    PROJE BİLGİLERİ:
    - Proje Adı: {test_data['project_name']}
    - Proje Açıklaması: {test_data['project_description']}
    - Proje İhtiyaçları: {test_data['project_needs']}

    EKİP ÜYELERİ:
    """
    
    for member in test_data['team_members']:
        prompt += f"""
    - {member['name']}:
      * Rol: {member['role']}
      * Günlük Çalışma Saati: {member['available_hours']} saat
      * Yetenekler: {', '.join(member['skills'])}
        """
    
    prompt += f"""

    GÖREV:
    Bu proje için detaylı görev planlaması yap. Her görev için:
    1. Görev başlığı (açık ve anlaşılır)
    2. Hangi kişiye atanacağı
    3. Tahmini süre (gün olarak)
    4. Başlangıç ve bitiş tarihi
    5. Görev açıklaması
    6. Öncelik seviyesi (low, medium, high, urgent)

    KURALLAR:
    - Görevler mantıklı sırayla olmalı (önce backend, sonra frontend)
    - Her kişinin günlük çalışma saatine göre süre hesapla
    - Görevler 1-14 gün arasında olmalı
    - Tarihler YYYY-MM-DD formatında olmalı
    - Bugünden başla (bugün: {datetime.now().strftime('%Y-%m-%d')})

    SADECE JSON formatında yanıtla, başka açıklama ekleme:

    {{
      "tasks": [
        {{
          "title": "Görev başlığı",
          "assigned_to": "Kullanıcı adı",
          "duration_days": 3,
          "start_date": "2025-07-28",
          "end_date": "2025-07-31",
          "description": "Detaylı görev açıklaması",
          "priority": "medium"
        }}
      ]
    }}
    """
    
    print(prompt)
    
    print("\n3. Beklenen Gemini Response")
    print("-" * 40)
    
    expected_response = {
        "status": "success",
        "tasks": [
            {
                "title": "Veritabanı tasarımı ve API geliştirme",
                "assigned_to": "Halitcan",
                "duration_days": 5,
                "start_date": "2025-07-28",
                "end_date": "2025-08-02",
                "description": "PostgreSQL veritabanı tasarımı, Django REST API geliştirme, kullanıcı yönetimi",
                "priority": "high"
            },
            {
                "title": "Frontend ana yapısı ve routing",
                "assigned_to": "Ayşe",
                "duration_days": 4,
                "start_date": "2025-07-30",
                "end_date": "2025-08-03",
                "description": "React uygulaması kurulumu, routing yapısı, temel bileşenler",
                "priority": "high"
            },
            {
                "title": "Ürün kataloğu ve sepet sistemi",
                "assigned_to": "Ayşe",
                "duration_days": 6,
                "start_date": "2025-08-04",
                "end_date": "2025-08-10",
                "description": "Ürün listeleme, filtreleme, sepet işlemleri, kullanıcı arayüzü",
                "priority": "medium"
            },
            {
                "title": "Ödeme sistemi entegrasyonu",
                "assigned_to": "Halitcan",
                "duration_days": 4,
                "start_date": "2025-08-11",
                "end_date": "2025-08-15",
                "description": "Ödeme gateway entegrasyonu, güvenlik önlemleri, test",
                "priority": "high"
            },
            {
                "title": "Admin paneli geliştirme",
                "assigned_to": "Ayşe",
                "duration_days": 3,
                "start_date": "2025-08-16",
                "end_date": "2025-08-19",
                "description": "Admin dashboard, ürün yönetimi, kullanıcı yönetimi",
                "priority": "medium"
            },
            {
                "title": "Test senaryoları ve QA",
                "assigned_to": "Mehmet",
                "duration_days": 4,
                "start_date": "2025-08-20",
                "end_date": "2025-08-24",
                "description": "Manuel testler, otomatik testler, hata raporlama",
                "priority": "medium"
            }
        ]
    }
    
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))
    
    print("\n4. Test Senaryosu")
    print("-" * 40)
    
    print("✅ Bu veriyi Gemini'ye gönder")
    print("✅ JSON response'u parse et")
    print("✅ Görevleri veritabanına kaydet")
    print("✅ Kullanıcılara görevleri ata")
    print("✅ Bildirimleri gönder")
    
    print("\n=== Test Senaryosu Tamamlandı ===")
    print("\nÖnemli Notlar:")
    print("• Gemini API key settings.py'de tanımlı")
    print("• Mevcut Gemini entegrasyonu kullanılıyor")
    print("• JSON response temizleme fonksiyonu mevcut")
    print("• Hata yönetimi eklenmiş")

if __name__ == "__main__":
    test_gemini_task_planning() 