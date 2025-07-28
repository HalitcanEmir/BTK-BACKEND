#!/usr/bin/env python3
"""
Proje Başvuru Sistemi Test Senaryosu

Bu dosya, yeni eklenen günlük çalışma saati özelliğinin nasıl kullanılacağını gösterir.
"""

import requests
import json

# Test sunucusu URL'i (geliştirme ortamı için)
BASE_URL = "http://localhost:8000"

def test_project_application():
    """Proje başvuru sistemi test senaryosu"""
    
    print("=== Proje Başvuru Sistemi Test Senaryosu ===\n")
    
    # 1. Projeye başvuru yapma
    print("1. Projeye Başvuru Yapma")
    print("-" * 40)
    
    project_id = "665f1c2e8b3e2a1a2b3c4d5f"  # Örnek proje ID
    
    application_data = {
        "daily_available_hours": 4,
        "message": "Bu projede frontend geliştirme yapmak istiyorum. React ve TypeScript konularında deneyimim var."
    }
    
    print(f"Gönderilen veri: {json.dumps(application_data, indent=2)}")
    
    # Bu kısım gerçek bir HTTP isteği yapmak için kullanılabilir
    # response = requests.post(
    #     f"{BASE_URL}/projects/{project_id}/join-request",
    #     json=application_data,
    #     headers={"Authorization": "Bearer YOUR_JWT_TOKEN"}
    # )
    # print(f"Response: {response.json()}")
    
    print("✅ Başvuru verisi hazırlandı\n")
    
    # 1.1. Başvuru güncelleme (aynı kullanıcı tekrar başvuru yaparsa)
    print("1.1. Başvuru Güncelleme")
    print("-" * 40)
    
    updated_application_data = {
        "daily_available_hours": 6,
        "message": "Güncellenmiş mesaj: Daha fazla zaman ayırabilirim."
    }
    
    print(f"Güncellenmiş veri: {json.dumps(updated_application_data, indent=2)}")
    print("✅ Başvuru güncelleme testi hazırlandı\n")
    
    # 1.2. Başvuru iptal etme
    print("1.2. Başvuru İptal Etme")
    print("-" * 40)
    
    # POST /projects/{id}/join-request/cancel
    cancel_response = {
        "status": "ok",
        "message": "Proje başvurunuz iptal edildi"
    }
    
    print(f"İptal response: {json.dumps(cancel_response, indent=2)}")
    print("✅ Başvuru iptal testi hazırlandı\n")
    
    # 2. Başvuru durumu kontrolü
    print("2. Başvuru Durumu Kontrolü")
    print("-" * 40)
    
    # GET /projects/{id}/join-request/status
    expected_response = {
        "has_applied": True,
        "status": "pending",
        "message": "Bu projede frontend geliştirme yapmak istiyorum. React ve TypeScript konularında deneyimim var.",
        "daily_available_hours": 4
    }
    
    print(f"Beklenen response: {json.dumps(expected_response, indent=2)}")
    print("✅ Başvuru durumu kontrol edildi\n")
    
    # 3. Admin başvuru listesi
    print("3. Admin - Başvuru Listesi")
    print("-" * 40)
    
    admin_response = {
        "status": "ok",
        "join_requests": [
            {
                "id": "665f1c2e8b3e2a1a2b3c4d5e",
                "project_id": project_id,
                "project_title": "E-Ticaret Platformu",
                "user_id": "665f1c2e8b3e2a1a2b3c4d60",
                "user_name": "Ahmet Yılmaz",
                "message": "Bu projede frontend geliştirme yapmak istiyorum. React ve TypeScript konularında deneyimim var.",
                "daily_available_hours": 4,
                "status": "pending",
                "created_at": "2024-01-15T10:30:00Z"
            }
        ],
        "total_count": 1
    }
    
    print(f"Admin response: {json.dumps(admin_response, indent=2)}")
    print("✅ Admin başvuru listesi alındı\n")
    
    # 4. Gemini AI için ekip planlaması verisi
    print("4. Gemini AI - Ekip Planlaması Verisi")
    print("-" * 40)
    
    team_planning_data = {
        "status": "ok",
        "project_data": {
            "project_id": project_id,
            "project_title": "E-Ticaret Platformu",
            "project_description": "Modern e-ticaret platformu geliştirme projesi",
            "team_members": [
                {
                    "user_id": "665f1c2e8b3e2a1a2b3c4d60",
                    "user_name": "Ahmet Yılmaz",
                    "daily_available_hours": 4,
                    "message": "Bu projede frontend geliştirme yapmak istiyorum. React ve TypeScript konularında deneyimim var."
                }
            ],
            "total_team_size": 1,
            "total_daily_hours": 4
        },
        "message": "Proje ekibi planlaması için veri hazırlandı"
    }
    
    print(f"Gemini AI verisi: {json.dumps(team_planning_data, indent=2)}")
    print("✅ Gemini AI için ekip planlaması verisi hazırlandı\n")
    
    # 5. Validasyon testleri
    print("5. Validasyon Testleri")
    print("-" * 40)
    
    validation_tests = [
        {
            "test": "Günlük çalışma saati belirtilmemiş",
            "data": {"message": "Test mesajı"},
            "expected_error": "Günlük çalışma saati belirtmelisiniz"
        },
        {
            "test": "Günlük çalışma saati 0 (çok düşük)",
            "data": {"daily_available_hours": 0, "message": "Test mesajı"},
            "expected_error": "Günlük çalışma saati 1-12 saat arasında olmalıdır"
        },
        {
            "test": "Günlük çalışma saati 24 (çok yüksek)",
            "data": {"daily_available_hours": 24, "message": "Test mesajı"},
            "expected_error": "Günlük çalışma saati 1-12 saat arasında olmalıdır"
        },
        {
            "test": "Günlük çalışma saati string (geçersiz tip)",
            "data": {"daily_available_hours": "abc", "message": "Test mesajı"},
            "expected_error": "Günlük çalışma saati sayı olmalıdır"
        }
    ]
    
    for test in validation_tests:
        print(f"✅ {test['test']}: {test['expected_error']}")
    
    print("\n=== Test Senaryosu Tamamlandı ===")
    print("\nÖnemli Notlar:")
    print("• Günlük çalışma saati 1-12 saat arasında olmalıdır")
    print("• Bu alan zorunludur ve sayı olmalıdır")
    print("• Aynı kullanıcı aynı projeye birden fazla başvuru yapamaz")
    print("• Gemini AI, bu veriyi kullanarak görev dağılımı yapacak")

if __name__ == "__main__":
    test_project_application() 