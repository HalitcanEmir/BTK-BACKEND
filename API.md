# BTK Backend API Dökümantasyonu

## Proje Başvuru Sistemi

### Projeye Başvuru Yapma

**Endpoint:** `POST /projects/{id}/join-request`

**Açıklama:** Bir projeye katılım başvurusu gönderir. Eğer kullanıcı daha önce başvuru yapmışsa, mevcut başvuru güncellenir.

**Gerekli Alanlar:**
- `daily_available_hours` (int, zorunlu): Günlük çalışma saati (1-12 arası)
- `message` (string, isteğe bağlı): Başvuru mesajı

**Örnek İstek:**
```json
{
  "daily_available_hours": 4,
  "message": "Bu projede frontend geliştirme yapmak istiyorum."
}
```

**Başarılı Response (Yeni Başvuru):**
```json
{
  "status": "ok",
  "message": "Proje başvurunuz alındı",
  "request_id": "665f1c2e8b3e2a1a2b3c4d5e"
}
```

**Başarılı Response (Güncelleme):**
```json
{
  "status": "ok",
  "message": "Proje başvurunuz güncellendi",
  "request_id": "665f1c2e8b3e2a1a2b3c4d5e"
}
```

### Başvuru İptal Etme

**Endpoint:** `POST /projects/{id}/join-request/cancel`

**Açıklama:** Kullanıcının proje başvurusunu iptal eder.

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Proje başvurunuz iptal edildi"
}
```

**Hatalı Response (Onaylanmış başvuru):**
```json
{
  "status": "error",
  "message": "Onaylanmış başvuru iptal edilemez"
}
```

### Başvuru Durumu Kontrolü

**Endpoint:** `GET /projects/{id}/join-request/status`

**Açıklama:** Kullanıcının proje başvuru durumunu kontrol eder.

**Başarılı Response:**
```json
{
  "has_applied": true,
  "status": "pending",
  "message": "Bu projede frontend geliştirme yapmak istiyorum.",
  "daily_available_hours": 4
}
```

### Admin - Proje Başvurularını Listeleme

**Endpoint:** `GET /projects/admin/join-requests`

**Açıklama:** Admin için tüm proje başvurularını listeler.

**Query Parametreleri:**
- `status` (string, isteğe bağlı): Filtreleme için (pending, approved, rejected)

**Başarılı Response:**
```json
{
  "status": "ok",
  "join_requests": [
    {
      "id": "665f1c2e8b3e2a1a2b3c4d5e",
      "project_id": "665f1c2e8b3e2a1a2b3c4d5f",
      "project_title": "E-Ticaret Platformu",
      "user_id": "665f1c2e8b3e2a1a2b3c4d60",
      "user_name": "Ahmet Yılmaz",
      "message": "Frontend geliştirme yapmak istiyorum",
      "daily_available_hours": 4,
      "status": "pending",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1
}
```

### Admin - Başvuru Onaylama

**Endpoint:** `POST /projects/admin/join-requests/{request_id}/approve`

**Açıklama:** Admin proje başvurusunu onaylar ve kullanıcıyı ekibe ekler.

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Proje başvurusu onaylandı ve kullanıcı ekibe eklendi",
  "user_name": "Ahmet Yılmaz",
  "project_title": "E-Ticaret Platformu"
}
```

### Admin - Başvuru Reddetme

**Endpoint:** `POST /projects/admin/join-requests/{request_id}/reject`

**Açıklama:** Admin proje başvurusunu reddeder.

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Proje başvurusu reddedildi"
}
```

### Proje Ekibi Planlaması Verisi

**Endpoint:** `GET /projects/{id}/team-planning-data`

**Açıklama:** Gemini AI için proje ekibi planlaması verisini hazırlar.

**Başarılı Response:**
```json
{
  "status": "ok",
  "project_data": {
    "project_id": "665f1c2e8b3e2a1a2b3c4d5f",
    "project_title": "E-Ticaret Platformu",
    "project_description": "Modern e-ticaret platformu",
    "team_members": [
      {
        "user_id": "665f1c2e8b3e2a1a2b3c4d60",
        "user_name": "Ahmet Yılmaz",
        "daily_available_hours": 4,
        "message": "Frontend geliştirme yapmak istiyorum"
      }
    ],
    "total_team_size": 1,
    "total_daily_hours": 4
  },
  "message": "Proje ekibi planlaması için veri hazırlandı"
}
```

---

## Kişi Ekleme

**Endpoint:** `/add/`

**Yöntem:** GET

**Parametreler:**
- `name` (string, zorunlu): Kişinin adı
- `age` (int, zorunlu): Kişinin yaşı

**Örnek İstek:**
```
/add/?name=Ali&age=30
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "id": "665f1c2e8b3e2a1a2b3c4d5e"
}
```

**Hatalı Response:**
```json
{
  "status": "error",
  "message": "name and age required"
}
```

---

## Kişi Listesi

**Endpoint:** `/list/`

**Yöntem:** GET

**Açıklama:** Sistemde kayıtlı tüm kişileri listeler.

**Örnek İstek:**
```
/list/
```

**Başarılı Response:**
```json
{
  "people": [
    {"id": "665f1c2e8b3e2a1a2b3c4d5e", "name": "Ali", "age": 30},
    {"id": "665f1c2e8b3e2a1a2b3c4d5f", "name": "Ayşe", "age": 25}
  ]
} 

---

## SSL/TLS Hataları

pymongo.errors.ServerSelectionTimeoutError: SSL handshake failed: ac-groyz4g-shard-00-02.eqsstlg.mongodb.net:27017: [SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error (_ssl.c:1028)

### Bu Hata Neden Olur?
1. **İnternet bağlantınızda veya ağınızda bir sorun olabilir.**
2. **MongoDB Atlas bağlantı URI'nızda bir hata olabilir.**
3. **Bilgisayarınızda SSL/TLS kütüphanelerinde bir eksiklik veya uyumsuzluk olabilir.**
4. **MongoDB Atlas tarafında IP erişim izni (IP Whitelist) kaldırılmış veya değişmiş olabilir.**
5. **Atlas cluster'ınızda bir bakım veya geçici bir problem olabilir.**
6. **Python veya pymongo/mongoengine sürümünüz ile Atlas'ın TLS/SSL gereksinimleri uyumsuz olabilir.**

---

## Kontrol Etmen Gerekenler

### 1. **Atlas IP Whitelist**
- MongoDB Atlas paneline gir.
- "Network Access" → "IP Access List" kısmında kendi IP adresinin ekli olduğundan emin ol.
- Eğer IP adresin değiştiyse, yeni IP'ni ekle veya `0.0.0.0/0` (herkese açık, test için) ekleyip tekrar dene.

### 2. **Atlas Cluster Durumu**
- Atlas panelinde cluster'ın "green/healthy" olduğundan emin ol.

### 3. **Bağlantı URI'si**
- `settings.py` veya bağlantı kurduğun dosyada URI'nın şu formatta olduğundan emin ol:
  ```
  mongodb+srv://<username>:<password>@ac-groyz4g-shard-00-00.eqsstlg.mongodb.net/<dbname>?retryWrites=true&w=majority
  ```
- Kullanıcı adı, şifre ve db adı doğru mu?

### 4. **Python ve pymongo/mongoengine Sürümü**
- Python 3.13 kullanıyorsun, bu çok yeni bir sürüm ve bazı kütüphaneler tam uyumlu olmayabilir.
- `pymongo` ve `mongoengine`'in en güncel sürümünü kullandığından emin ol:
  ```
  pip install --upgrade pymongo mongoengine
  ```

### 5. **Bilgisayarında SSL/TLS Sorunu**
- Windows'ta bazen OpenSSL kütüphaneleri eksik olabiliyor.
- Güncel bir Python ve pip ile kurulum yaptığından emin ol.

### 6. **Atlas'ta TLS/SSL Zorunlu**
- Atlas bağlantıları her zaman TLS/SSL ister. Bağlantı URI'ında `ssl=true` veya `tls=true` parametresi olmalı (genelde otomatik olur).

---

## Hızlı Kontrol Listesi

1. **Atlas IP Whitelist**: IP adresin eklendi mi?
2. **Atlas Cluster**: Çalışıyor mu?
3. **Bağlantı URI**: Doğru mu, kullanıcı/şifre doğru mu?
4. **Kütüphane Sürümü**: pymongo ve mongoengine güncel mi?
5. **Python Sürümü**: Çok yeni bir sürüm kullanıyorsan, 3.10 veya 3.11 ile dene.
6. **İnternet**: VPN, proxy, firewall engeli var mı?

---

## Ekstra: Hızlı Test

Aşağıdaki kodu terminalde çalıştırıp bağlantı test edebilirsin:
```python
from pymongo import MongoClient

client = MongoClient("mongodb+srv://<username>:<password>@ac-groyz4g-shard-00-00.eqsstlg.mongodb.net/test?retryWrites=true&w=majority")
print(client.list_database_names())
```
Kendi kullanıcı adı ve şifreni gir. Hata alırsan, hata mesajını paylaşabilirsin.

---

**Tüm bu adımları kontrol et, hala sorun yaşarsan bağlantı URI'nı (şifreyi gizleyerek) ve settings.py'deki ilgili kısmı paylaşabilirsin. Daha detaylı yardımcı olabilirim!** 

---

## Görev Planlama Sistemi

### Gemini AI ile Görev Oluşturma

**Endpoint:** `POST /projects/{id}/generate-tasks`

**Açıklama:** Gemini AI kullanarak proje için otomatik görev planlaması yapar.

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "2 görev başarıyla oluşturuldu",
  "tasks": [
    {
      "title": "Kullanıcı kayıt/giriş sistemi",
      "assigned_to": "Halitcan",
      "duration_days": 3,
      "start_date": "2025-07-28",
      "end_date": "2025-07-31",
      "description": "Kullanıcı kayıt ve giriş sistemi geliştirme",
      "priority": "high"
    }
  ],
  "total_tasks": 2
}
```

### Kullanıcı Görevlerini Listeleme

**Endpoint:** `GET /projects/tasks/my`

**Query Parametreleri:**
- `status` (string, isteğe bağlı): Filtreleme için (to-do, in-progress, done)
- `priority` (string, isteğe bağlı): Filtreleme için (low, medium, high, urgent)

**Başarılı Response:**
```json
{
  "status": "ok",
  "tasks": [
    {
      "id": "665f1c2e8b3e2a1a2b3c4d5e",
      "title": "Kullanıcı kayıt/giriş sistemi",
      "description": "Kullanıcı kayıt ve giriş sistemi geliştirme",
      "project_id": "665f1c2e8b3e2a1a2b3c4d5f",
      "project_title": "E-Ticaret Platformu",
      "status": "in-progress",
      "priority": "high",
      "start_date": "2025-07-28T00:00:00Z",
      "end_date": "2025-07-31T00:00:00Z",
      "duration_days": 3,
      "assigned_by": "Admin User",
      "created_at": "2025-07-28T10:30:00Z",
      "completed_at": null,
      "completion_notes": null,
      "recent_logs": [
        {
          "action": "started",
          "notes": "Göreve başladım",
          "created_at": "2025-07-28T10:30:00Z"
        }
      ],
      "is_overdue": false
    }
  ],
  "total_count": 1
}
```

### Proje Görevlerini Listeleme (Admin)

**Endpoint:** `GET /projects/{id}/tasks`

**Başarılı Response:**
```json
{
  "status": "ok",
  "tasks": [
    {
      "id": "665f1c2e8b3e2a1a2b3c4d5e",
      "title": "Kullanıcı kayıt/giriş sistemi",
      "description": "Kullanıcı kayıt ve giriş sistemi geliştirme",
      "assigned_user_id": "665f1c2e8b3e2a1a2b3c4d60",
      "assigned_user_name": "Halitcan",
      "status": "in-progress",
      "priority": "high",
      "start_date": "2025-07-28T00:00:00Z",
      "end_date": "2025-07-31T00:00:00Z",
      "duration_days": 3,
      "assigned_by": "Admin User",
      "created_at": "2025-07-28T10:30:00Z",
      "completed_at": null,
      "completion_notes": null,
      "is_overdue": false
    }
  ],
  "statistics": {
    "total_tasks": 5,
    "completed_tasks": 2,
    "pending_tasks": 3,
    "overdue_tasks": 1,
    "completion_rate": 40.0
  }
}
```

### Görev Durumu Güncelleme

**Endpoint:** `POST /projects/tasks/{task_id}/status`

**Body:**
```json
{
  "status": "done",
  "notes": "Görev başarıyla tamamlandı"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Görev durumu 'in-progress' -> 'done' olarak güncellendi",
  "task_id": "665f1c2e8b3e2a1a2b3c4d5e",
  "new_status": "done"
}
```

### Görev Log Ekleme

**Endpoint:** `POST /projects/tasks/{task_id}/log`

**Body:**
```json
{
  "action": "started",
  "notes": "Göreve başladım"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Log başarıyla eklendi",
  "log_id": "665f1c2e8b3e2a1a2b3c4d5f"
}
```

### Görev Bildirimleri

**Endpoint:** `GET /projects/notifications/tasks`

**Başarılı Response:**
```json
{
  "status": "ok",
  "notifications": [
    {
      "type": "overdue",
      "title": "Süresi Geçen Görev",
      "message": "\"Kullanıcı kayıt/giriş sistemi\" görevinin süresi geçti",
      "task_id": "665f1c2e8b3e2a1a2b3c4d5e",
      "project_title": "E-Ticaret Platformu",
      "days_overdue": 2
    },
    {
      "type": "upcoming",
      "title": "Yaklaşan Görev",
      "message": "\"Proje kart tasarımı\" görevinin bitiş tarihi yaklaşıyor",
      "task_id": "665f1c2e8b3e2a1a2b3c4d5f",
      "project_title": "E-Ticaret Platformu",
      "days_until_deadline": 1
    }
  ],
  "total_count": 2
}
```

### Performans Skoru

**Endpoint:** `GET /projects/performance/score`

**Başarılı Response:**
```json
{
  "status": "ok",
  "user_id": "665f1c2e8b3e2a1a2b3c4d60",
  "user_name": "Halitcan",
  "performance_score": 750,
  "performance_level": "İyi",
  "statistics": {
    "total_tasks": 10,
    "completed_tasks": 8,
    "overdue_tasks": 1,
    "on_time_tasks": 7,
    "completion_rate": 80.0,
    "on_time_rate": 87.5
  },
  "score_breakdown": {
    "base_score": 100,
    "completion_bonus": 80,
    "on_time_bonus": 35,
    "overdue_penalty": 15,
    "total_score": 750
  }
}
```

### Performans Sıralaması

**Endpoint:** `GET /projects/performance/leaderboard`

**Başarılı Response:**
```json
{
  "status": "ok",
  "leaderboard": [
    {
      "user_id": "665f1c2e8b3e2a1a2b3c4d60",
      "user_name": "Halitcan",
      "performance_score": 750,
      "total_tasks": 10,
      "completed_tasks": 8,
      "completion_rate": 80.0
    },
    {
      "user_id": "665f1c2e8b3e2a1a2b3c4d61",
      "user_name": "Ayşe",
      "performance_score": 650,
      "total_tasks": 8,
      "completed_tasks": 6,
      "completion_rate": 75.0
    }
  ],
  "total_participants": 2
}
```

--- 

### Görev İlerleme Güncelleme

**Endpoint:** `POST /projects/tasks/{task_id}/progress`

**Açıklama:** Kullanıcının görev ilerleme durumunu günceller.

**Body:**
```json
{
  "progress_percentage": 75,
  "user_notes": "API entegrasyonu tamamlandı, test aşamasındayım",
  "actual_hours": 12
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Görev ilerlemesi %50 -> %75 olarak güncellendi",
  "task_id": "665f1c2e8b3e2a1a2b3c4d5e",
  "progress_percentage": 75
}
```

### Kullanıcı Görev Dashboard'u

**Endpoint:** `GET /projects/tasks/dashboard`

**Açıklama:** Kullanıcının görev istatistiklerini ve yaklaşan görevlerini getirir.

**Başarılı Response:**
```json
{
  "status": "ok",
  "statistics": {
    "total_tasks": 10,
    "completed_tasks": 6,
    "in_progress_tasks": 2,
    "overdue_tasks": 1,
    "upcoming_tasks": 1
  },
  "upcoming_deadlines": [
    {
      "task_id": "665f1c2e8b3e2a1a2b3c4d5e",
      "title": "API Entegrasyonu",
      "days_until_deadline": 2,
      "is_overdue": false
    }
  ],
  "performance": {
    "reliability_score": 750,
    "total_tasks": 10,
    "completed_tasks": 6,
    "overdue_tasks": 1,
    "on_time_tasks": 5,
    "completion_rate": 60.0,
    "on_time_rate": 83.33
  }
}
```

### Gelişmiş Görev Bildirimleri

**Endpoint:** `GET /projects/notifications/tasks/advanced`

**Açıklama:** Detaylı görev bildirimlerini getirir (başlama, gecikme, yaklaşan, düşük ilerleme).

**Başarılı Response:**
```json
{
  "status": "ok",
  "notifications": [
    {
      "type": "task_started",
      "title": "Görev Başladı",
      "message": "\"API Entegrasyonu\" görevin başladı",
      "task_id": "665f1c2e8b3e2a1a2b3c4d5e",
      "project_title": "E-Ticaret Platformu",
      "priority": "high",
      "days_remaining": 3
    },
    {
      "type": "overdue",
      "title": "Süresi Geçen Görev",
      "message": "\"Frontend Tasarımı\" görevinin süresi 2 gün geçti",
      "task_id": "665f1c2e8b3e2a1a2b3c4d5f",
      "project_title": "E-Ticaret Platformu",
      "days_overdue": 2,
      "priority": "urgent"
    },
    {
      "type": "low_progress",
      "title": "Düşük İlerleme",
      "message": "\"Test Senaryoları\" görevinde ilerleme düşük (%20)",
      "task_id": "665f1c2e8b3e2a1a2b3c4d60",
      "project_title": "E-Ticaret Platformu",
      "progress_percentage": 20,
      "days_remaining": 1
    }
  ],
  "total_count": 3,
  "urgent_count": 1,
  "upcoming_count": 1
}
```

### Kullanıcı Performans Analizi

**Endpoint:** `GET /projects/tasks/analytics`

**Açıklama:** Kullanıcının detaylı performans analizini getirir.

**Başarılı Response:**
```json
{
  "status": "ok",
  "current_month": {
    "total_tasks": 5,
    "completed_tasks": 3,
    "overdue_tasks": 1,
    "completion_rate": 60.0
  },
  "task_categories": {
    "Backend": {
      "total": 4,
      "completed": 2,
      "overdue": 1,
      "avg_completion_time": 3.5
    },
    "Frontend": {
      "total": 3,
      "completed": 2,
      "overdue": 0,
      "avg_completion_time": 2.0
    }
  },
  "monthly_performance": [
    {
      "month": "2025-07",
      "total_tasks": 5,
      "completed_tasks": 3,
      "overdue_tasks": 1,
      "completion_rate": 60.0
    }
  ],
  "overall_stats": {
    "reliability_score": 750,
    "total_tasks": 10,
    "completed_tasks": 6,
    "overdue_tasks": 1,
    "on_time_tasks": 5,
    "average_completion_time": 3.2,
    "completion_rate": 60.0,
    "on_time_rate": 83.33
  }
}
```

--- 

### Proje Timeline Analizi

**Endpoint:** `POST /projects/{project_id}/generate-timeline`

**Açıklama:** Gemini AI ile proje timeline analizi yapar.

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Proje timeline analizi tamamlandı. MVP: 2025-08-05",
  "timeline": {
    "mvp_deadline": "2025-08-05",
    "full_project_deadline": "2025-08-14",
    "milestone_list": [
      {
        "date": "2025-07-30",
        "description": "Backend API sistemi tamamlandı",
        "type": "development"
      },
      {
        "date": "2025-08-05",
        "description": "MVP hazır - temel özellikler çalışıyor",
        "type": "mvp"
      },
      {
        "date": "2025-08-14",
        "description": "Tüm proje tamamlandı",
        "type": "launch"
      }
    ],
    "riskli_gorevler": [
      {
        "title": "Kullanıcı arayüzü geliştirme",
        "reason": "Frontend geliştiricinin günlük çalışma süresi yetersiz olabilir",
        "risk_level": "medium"
      }
    ]
  },
  "total_tasks": 6,
  "timeline_id": "688747b1b837ea193f8604e0"
}
```

### Proje Timeline Görüntüleme

**Endpoint:** `GET /projects/{project_id}/timeline`

**Açıklama:** Proje timeline'ını getirir.

**Başarılı Response:**
```json
{
  "status": "ok",
  "project_title": "E-Ticaret Platformu",
  "timeline": {
    "id": "688747b1b837ea193f8604e0",
    "mvp_deadline": "2025-08-05",
    "full_project_deadline": "2025-08-14",
    "created_at": "2025-07-28",
    "risk_level": "medium",
    "total_tasks": 6,
    "completed_tasks": 2,
    "pending_tasks": 4
  },
  "milestones": [
    {
      "id": "688747b1b837ea193f8604e1",
      "date": "2025-07-30",
      "description": "Backend API sistemi tamamlandı",
      "type": "development",
      "status": "pending",
      "completed_at": null
    }
  ],
  "risks": [
    {
      "id": "688747b1b837ea193f8604e2",
      "task_title": "Kullanıcı arayüzü geliştirme",
      "reason": "Frontend geliştiricinin günlük çalışma süresi yetersiz olabilir",
      "risk_level": "medium",
      "mitigation_strategy": null
    }
  ],
  "task_stats": {
    "total_tasks": 6,
    "completed_tasks": 2,
    "in_progress_tasks": 3,
    "overdue_tasks": 1,
    "avg_progress": 45.5
  }
}
```

### Kullanıcı Timeline Katkısı

**Endpoint:** `GET /projects/timeline/contribution`

**Açıklama:** Kullanıcının timeline katkısını getirir.

**Başarılı Response:**
```json
{
  "status": "ok",
  "timeline_contribution": [
    {
      "project_title": "E-Ticaret Platformu",
      "project_id": "68873f71b8d65f255b958a3f",
      "tasks": [
        {
          "id": "688747b1b837ea193f8604d0",
          "title": "Backend Altyapısı Kurulumu",
          "start_date": "2025-07-28",
          "end_date": "2025-08-03",
          "duration_days": 7,
          "status": "in-progress",
          "progress_percentage": 75,
          "is_overdue": false
        }
      ],
      "total_duration": 7,
      "completed_tasks": 0,
      "overdue_tasks": 0,
      "timeline": {
        "mvp_deadline": "2025-08-05",
        "full_project_deadline": "2025-08-14",
        "risk_level": "medium"
      }
    }
  ],
  "total_projects": 1
}
```

--- 

### Email Doğrulama Kodu Gönderme

**Endpoint:** `POST /api/auth/send-verification-code`

**Açıklama:** Email adresine doğrulama kodu gönderir.

**Body:**
```json
{
  "email": "user@example.com"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Doğrulama kodu email adresinize gönderildi",
  "email": "user@example.com"
}
```

### Kullanıcı Kaydı (Email Doğrulama ile)

**Endpoint:** `POST /api/auth/register`

**Açıklama:** Kullanıcı kaydı yapar ve email doğrulama kodu gönderir.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "user_type": ["developer"],
  "github_token": "optional",
  "linkedin_token": "optional",
  "card_token": "optional"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Email doğrulama kodu gönderildi. Lütfen email'inizi kontrol edin.",
  "user": {
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": ["developer"],
    "message": "Email doğrulama kodu gönderildi. Lütfen email'inizi kontrol edin."
  },
  "requires_verification": true
}
```

**Not:** Bu endpoint artık doğrudan kullanıcı oluşturmaz, sadece email doğrulama kodu gönderir. Kullanıcı kaydı için `/verify-email-and-register` endpoint'ini kullanın.

---

### Email Doğrulama ve Kayıt

**Endpoint:** `POST /api/auth/verify-email-and-register`

**Açıklama:** Doğrulama kodunu kontrol eder ve kullanıcıyı kaydeder.

**Body:**
```json
{
  "email": "user@example.com",
  "verification_code": "123456",
  "full_name": "John Doe",
  "password": "securepassword123",
  "user_type": ["developer"]
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Kayıt başarılı! Hoş geldiniz.",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": ["developer"]
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Doğrulama Kodunu Tekrar Gönderme

**Endpoint:** `POST /api/auth/resend-verification-code`

**Açıklama:** Doğrulama kodunu tekrar gönderir.

**Body:**
```json
{
  "email": "user@example.com"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Yeni doğrulama kodu gönderildi",
  "email": "user@example.com"
}
```

--- 

### Şifre Sıfırlama Kodu Gönderme

**Endpoint:** `POST /api/auth/send-password-reset-code`

**Açıklama:** Email adresine şifre sıfırlama kodu gönderir.

**Body:**
```json
{
  "email": "user@example.com"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Şifre sıfırlama kodu email adresinize gönderildi. Lütfen email'inizi kontrol edin.",
  "email": "user@example.com"
}
```

### Şifre Sıfırlama Kodu Doğrulama ve Şifre Değiştirme

**Endpoint:** `POST /api/auth/verify-reset-code-and-change-password`

**Açıklama:** Sıfırlama kodunu doğrular ve yeni şifre belirler.

**Body:**
```json
{
  "email": "user@example.com",
  "reset_code": "123456",
  "new_password": "yenişifre123"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Şifreniz başarıyla güncellendi!",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### Şifre Sıfırlama Kodunu Tekrar Gönderme

**Endpoint:** `POST /api/auth/resend-password-reset-code`

**Açıklama:** Şifre sıfırlama kodunu tekrar gönderir.

**Body:**
```json
{
  "email": "user@example.com"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Yeni şifre sıfırlama kodu gönderildi. Lütfen email'inizi kontrol edin.",
  "email": "user@example.com"
}
```

--- 