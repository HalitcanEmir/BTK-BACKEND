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

## Fikir Analizi Sistemi

### Proje Fikri Analizi

**Endpoint:** `POST /ideas/analyze-project/`

**Açıklama:** Girilen proje fikrini Gemini AI ile analiz eder ve teknoloji önerileri, ekip büyüklüğü, süre tahmini gibi bilgiler verir.

**Headers:** `Authorization: Bearer <token>` (opsiyonel)

**Body:**
```json
{
  "description": "E-ticaret platformu geliştirmek istiyorum. Kullanıcılar ürün satabilir, alabilir ve ödeme yapabilir. Ayrıca AI destekli ürün önerisi sistemi olsun."
}
```

**Başarılı Response:**
```json
{
  "success": true,
  "analysis": {
    "technologies": ["Python", "Django", "React", "PostgreSQL", "Redis", "OpenAI API"],
    "skill_level": "Orta",
    "team_size": 4,
    "roles": ["Backend Developer", "Frontend Developer", "DevOps Engineer", "AI/ML Engineer"],
    "estimated_duration": "3-4 hafta",
    "notes": "AI öneri sistemi için veri toplama ve model eğitimi kritik. Ödeme sistemi entegrasyonu için güvenlik önlemleri alınmalı."
  }
}
```

**Hatalı Response:**
```json
{
  "success": false,
  "error": "Proje açıklaması gerekli."
}
```

### Proje Analizi Kaydetme

**Endpoint:** `POST /ideas/save-analysis/`

**Açıklama:** Yapılan proje analizini veritabanına kaydeder.

**Headers:** `Authorization: Bearer <token>` (opsiyonel)

**Body:**
```json
{
  "idea_id": "507f1f77bcf86cd799439011",
  "analysis": {
    "technologies": ["Python", "Django", "React", "PostgreSQL"],
    "skill_level": "Orta",
    "team_size": 3,
    "roles": ["Backend Developer", "Frontend Developer", "DevOps Engineer"],
    "estimated_duration": "2-3 hafta",
    "notes": "API güvenliği ve veri doğrulama kritik."
  }
}
```

**Başarılı Response:**
```json
{
  "success": true,
  "message": "Proje analizi başarıyla kaydedildi.",
  "analysis_id": "507f1f77bcf86cd799439012"
}
```

**Hatalı Response:**
```json
{
  "success": false,
  "error": "Idea ID ve analiz verisi gerekli."
}
```

### Fikir Gönderme (Analiz ile)

**Endpoint:** `POST /ideas/submit-idea`

**Açıklama:** Yeni fikir gönderir ve otomatik analiz yapar.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "title": "AI Destekli E-Ticaret Platformu",
  "description": "Kullanıcıların ürün satıp alabileceği, AI destekli öneri sistemi olan modern e-ticaret platformu.",
  "category": "e-commerce",
  "license_accepted": true,
  "auto_analyze": true
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Fikir başarıyla gönderildi ve analiz edildi.",
  "idea": {
    "id": "507f1f77bcf86cd799439011",
    "title": "AI Destekli E-Ticaret Platformu",
    "description": "Kullanıcıların ürün satıp alabileceği, AI destekli öneri sistemi olan modern e-ticaret platformu.",
    "category": "e-commerce",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "analysis": {
    "technologies": ["Python", "Django", "React", "PostgreSQL", "OpenAI API"],
    "skill_level": "Orta",
    "team_size": 4,
    "roles": ["Backend Developer", "Frontend Developer", "DevOps Engineer", "AI/ML Engineer"],
    "estimated_duration": "3-4 hafta",
    "notes": "AI öneri sistemi için veri toplama ve model eğitimi kritik."
  }
}
```

---

## Yatırım Sistemi

### Yatırım Teklifi Gönderme

**Endpoint:** `POST /projects/{id}/invest`

**Açıklama:** Yatırımcılar projelere yatırım teklifi gönderir.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "amount": 5000,
  "description": "Bu projeye güveniyorum ve yatırım yapmak istiyorum."
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Yatırım teklifi gönderildi",
  "offer_id": "0"
}
```

**Hatalı Response:**
```json
{
  "status": "error",
  "message": "Sadece yatırımcılar yatırım yapabilir"
}
```

### Yatırım Teklifini Onaylama

**Endpoint:** `POST /projects/{project_id}/investment-offers/{offer_id}/approve`

**Açıklama:** Proje sahibi yatırım teklifini onaylar.

**Headers:** `Authorization: Bearer <token>`

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Yatırım teklifi onaylandı"
}
```

### Yatırım Teklifini Reddetme

**Endpoint:** `POST /projects/{project_id}/investment-offers/{offer_id}/reject`

**Açıklama:** Proje sahibi yatırım teklifini reddeder.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "reason": "Şu an için yatırıma ihtiyacımız yok."
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Yatırım teklifi reddedildi"
}
```

### Proje Yatırım Tavsiyesi

**Endpoint:** `GET /projects/{id}/investment-advice`

**Açıklama:** Gemini AI ile proje için yatırım tavsiyesi alır.

**Headers:** `Authorization: Bearer <token>` (opsiyonel)

**Başarılı Response:**
```json
{
  "status": "ok",
  "advice": {
    "investment_recommendation": "Önerilen",
    "risk_level": "Orta",
    "potential_return": "Yüksek",
    "investment_amount": "5000-10000 TL",
    "reasoning": "Proje teknolojik açıdan güçlü ve pazar potansiyeli var.",
    "risks": ["Rekabet yoğun", "Teknoloji riski"],
    "opportunities": ["Büyüme potansiyeli", "Teknoloji avantajı"]
  }
}
```

---

## Proje AI Analizi

### Proje AI Analizi

**Endpoint:** `GET /projects/{id}/analyze`

**Açıklama:** Gemini AI ile proje detaylı analizi yapar.

**Headers:** `Authorization: Bearer <token>` (opsiyonel)

**Başarılı Response:**
```json
{
  "status": "ok",
  "analysis": {
    "market_analysis": "E-ticaret pazarı büyüyor",
    "technical_feasibility": "Yüksek",
    "competitive_advantage": "AI destekli öneri sistemi",
    "development_challenges": ["Ölçeklenebilirlik", "Güvenlik"],
    "success_probability": "75%",
    "recommendations": [
      "MVP ile başlayın",
      "Kullanıcı geri bildirimi toplayın",
      "Güvenlik önlemlerini artırın"
    ]
  }
}
```

### Proje Beğeni Sistemi

**Endpoint:** `POST /projects/{id}/like`

**Açıklama:** Projeyi beğenir veya beğenmekten vazgeçer.

**Headers:** `Authorization: Bearer <token>`

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Proje beğenildi",
  "likes_count": 15
}
```

### Proje Liderlik Tablosu

**Endpoint:** `GET /projects/leaderboard`

**Açıklama:** En çok beğenilen projeleri listeler.

**Başarılı Response:**
```json
{
  "status": "ok",
  "leaderboard": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "AI Destekli E-Ticaret Platformu",
      "likes_count": 25,
      "owner_name": "Ahmet Yılmaz",
      "category": "e-commerce"
    }
  ]
}
```

---

## Proje Tamamlama Sistemi

### Proje Tamamlama İsteği

**Endpoint:** `POST /projects/{id}/request-completion`

**Açıklama:** Proje sahibi projeyi tamamlandı olarak işaretlemek için istek gönderir.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "completion_notes": "Tüm özellikler tamamlandı ve test edildi.",
  "demo_url": "https://demo.example.com",
  "github_url": "https://github.com/user/project"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Tamamlama isteği gönderildi",
  "request_id": "507f1f77bcf86cd799439012"
}
```

### Tamamlama İsteklerini Listeleme (Admin)

**Endpoint:** `GET /projects/completion-requests`

**Açıklama:** Admin için tüm tamamlama isteklerini listeler.

**Headers:** `Authorization: Bearer <token>`

**Başarılı Response:**
```json
{
  "status": "ok",
  "requests": [
    {
      "id": "507f1f77bcf86cd799439012",
      "project_id": "507f1f77bcf86cd799439011",
      "project_title": "AI Destekli E-Ticaret Platformu",
      "owner_name": "Ahmet Yılmaz",
      "completion_notes": "Tüm özellikler tamamlandı",
      "demo_url": "https://demo.example.com",
      "github_url": "https://github.com/user/project",
      "status": "pending",
      "requested_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Tamamlama İsteğini Onaylama (Admin)

**Endpoint:** `POST /projects/{project_id}/completion-requests/{request_id}/approve`

**Açıklama:** Admin proje tamamlama isteğini onaylar.

**Headers:** `Authorization: Bearer <token>`

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Proje tamamlandı olarak onaylandı"
}
```

### Tamamlama İsteğini Reddetme (Admin)

**Endpoint:** `POST /projects/{project_id}/completion-requests/{request_id}/reject`

**Açıklama:** Admin proje tamamlama isteğini reddeder.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "reason": "Eksik özellikler var, tamamlanması gerekiyor."
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Tamamlama isteği reddedildi"
}
```

---

## Magic Link Giriş Sistemi

### Magic Link İsteği

**Endpoint:** `POST /demo/request-login`

**Açıklama:** Kullanıcı email ile giriş ister, magic link gönderilir.

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
  "message": "Magic link gönderildi"
}
```

### Magic Link ile Giriş

**Endpoint:** `GET /demo/verify-login?token={token}`

**Açıklama:** Magic link token'ı ile giriş yapar.

**Başarılı Response:**
```json
{
  "status": "ok",
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_developer": true,
    "is_investor": false,
    "linkedin_connected": false,
    "github_connected": false,
    "card_verified": false,
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

---

## Basit Endpoint'ler

### Bildirim Merkezi

**Endpoint:** `GET /api/notifications/`

**Açıklama:** Kullanıcının bildirimlerini listeler.

**Başarılı Response:**
```json
{
  "message": "Bildirim Merkezi"
}
```

### Hata Sayfaları

**Endpoint:** `GET /api/notifications/404`

**Açıklama:** Bulunamayan sayfa.

**Response:**
```json
{
  "message": "404 Not Found"
}
```

**Endpoint:** `GET /api/notifications/403`

**Açıklama:** Yetkisiz erişim.

**Response:**
```json
{
  "message": "403 Forbidden"
}
```

**Endpoint:** `GET /api/notifications/maintenance`

**Açıklama:** Sistem bakımda.

**Response:**
```json
{
  "message": "Bakım Sayfası"
}
```

### Topluluk Endpoint'leri

**Endpoint:** `GET /api/community/blog`

**Açıklama:** Blog yazıları ve duyurular.

**Response:**
```json
{
  "message": "Blog / Duyurular"
}
```

**Endpoint:** `GET /api/community/faq`

**Açıklama:** Sıkça sorulan sorular.

**Response:**
```json
{
  "message": "SSS"
}
```

**Endpoint:** `GET /api/community/social`

**Açıklama:** Youtube, etkinlik bağlantıları.

**Response:**
```json
{
  "message": "Topluluk Sayfası"
}
```

**Endpoint:** `GET /api/community/mentorship`

**Açıklama:** Mentorluk başvuru formu.

**Response:**
```json
{
  "message": "Mentorluk Başvuru Sayfası"
}
```

### Yatırım Endpoint'leri

**Endpoint:** `GET /api/investments/become`

**Açıklama:** Yatırımcı olma başvuru sayfası.

**Response:**
```json
{
  "message": "Yatırımcı Ol Sayfası"
}
```

**Endpoint:** `GET /api/investments/explore`

**Açıklama:** Yatırım yapılabilir projeleri listeler.

**Response:**
```json
{
  "message": "Proje Keşfet Sayfası"
}
```

**Endpoint:** `GET /api/investments/following`

**Açıklama:** Kullanıcının takip ettiği projeler.

**Response:**
```json
{
  "message": "Takip Ettiğim Projeler"
}
```

**Endpoint:** `POST /api/investments/offer`

**Açıklama:** Yatırım teklifi gönderme işlemi.

**Response:**
```json
{
  "message": "Yatırım Teklifi Gönderme Sayfası"
}
```

### Yasal Endpoint'ler

**Endpoint:** `GET /api/legal/terms`

**Açıklama:** Platformun kullanım şartları.

**Response:**
```json
{
  "message": "Kullanım Şartları"
}
```

**Endpoint:** `GET /api/legal/privacy`

**Açıklama:** Gizlilik politikası.

**Response:**
```json
{
  "message": "Gizlilik Politikası"
}
```

**Endpoint:** `GET /api/legal/cookies`

**Açıklama:** Çerez politikası.

**Response:**
```json
{
  "message": "Çerez Politikası"
}
```

### Ana Sayfa Endpoint'leri

**Endpoint:** `GET /api/core/home`

**Açıklama:** Platformun ana sayfası.

**Response:**
```json
{
  "message": "Ana Sayfa"
}
```

**Endpoint:** `GET /api/core/service`

**Açıklama:** Platformun sunduğu hizmetler.

**Response:**
```json
{
  "message": "Hizmetimiz"
}
```

**Endpoint:** `GET /api/core/about`

**Açıklama:** Platform hakkında bilgiler.

**Response:**
```json
{
  "message": "Hakkımızda"
}
```

**Endpoint:** `GET /api/core/contact`

**Açıklama:** İletişim bilgileri.

**Response:**
```json
{
  "message": "İletişim"
}
```

---

## Demo Endpoint'leri

### Kişi Ekleme

**Endpoint:** `GET /demo/add/`

**Açıklama:** Yeni bir kişi ekler.

**Parametreler:**
- `name` (string, zorunlu): Kişinin adı
- `age` (int, zorunlu): Kişinin yaşı

**Örnek İstek:**
```
/demo/add/?name=Ali&age=30
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

### Kişi Listesi

**Endpoint:** `GET /demo/list/`

**Açıklama:** Sistemde kayıtlı tüm kişileri listeler.

**Örnek İstek:**
```
/demo/list/
```

**Başarılı Response:**
```json
{
  "people": [
    {"id": "665f1c2e8b3e2a1a2b3c4d5e", "name": "Ali", "age": 30},
    {"id": "665f1c2e8b3e2a1a2b3c4d5f", "name": "Ayşe", "age": 25}
  ]
}
```

---

## Email Test Sistemi

### Email Ayarlarını Test Etme

**Endpoint:** `POST /api/auth/test-email-settings`

**Açıklama:** Email ayarlarını test eder ve test email'i gönderir.

**Headers:** `Authorization: Bearer <token>` (admin gerekli)

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Test email başarıyla gönderildi",
  "email_info": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "test@example.com",
    "tls_enabled": true
  }
}
```

**Hatalı Response:**
```json
{
  "status": "error",
  "message": "Email gönderme hatası: Authentication failed"
}
```

---

## Debug Endpoint'leri

### Kullanıcı Listesi (Debug)

**Endpoint:** `GET /projects/debug/users`

**Açıklama:** Sistemdeki tüm kullanıcıları listeler (debug amaçlı).

**Headers:** `Authorization: Bearer <token>` (admin gerekli)

**Başarılı Response:**
```json
{
  "status": "ok",
  "users": [
    {
      "id": "507f1f77bcf86cd799439011",
      "email": "user@example.com",
      "full_name": "John Doe",
      "user_type": ["developer"],
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1
}
```

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

### Profil Güncelleme

**Endpoint:** `POST /api/auth/update-profile`

**Açıklama:** Kullanıcı profilini günceller.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "full_name": "John Doe",
  "bio": "Full-stack developer with 5 years experience",
  "location": "Istanbul, Turkey",
  "website": "https://johndoe.com",
  "phone": "+90 555 123 4567",
  "github_username": "johndoe",
  "linkedin_username": "johndoe",
  "twitter_username": "johndoe"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Profil başarıyla güncellendi",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "john@example.com",
    "full_name": "John Doe",
    "bio": "Full-stack developer with 5 years experience",
    "location": "Istanbul, Turkey",
    "website": "https://johndoe.com",
    "phone": "+90 555 123 4567",
    "github_username": "johndoe",
    "linkedin_username": "johndoe",
    "twitter_username": "johndoe",
    "avatar": "/media/avatars/avatar_123.jpg"
  }
}
```

### Avatar Yükleme

**Endpoint:** `POST /api/auth/upload-avatar`

**Açıklama:** Kullanıcı avatarını yükler.

**Headers:** `Authorization: Bearer <token>`

**Body:** `multipart/form-data`
- `avatar`: Image file (JPEG, PNG, GIF, max 5MB)

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Avatar başarıyla yüklendi",
  "avatar_url": "/media/avatars/avatar_123_abc12345.jpg"
}
```

### Hesap Silme

**Endpoint:** `POST /api/auth/delete-account`

**Açıklama:** Kullanıcı hesabını siler (soft delete).

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "password": "currentpassword123"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Hesabınız başarıyla silindi"
}
```

### Arkadaşlık İsteği Gönderme

**Endpoint:** `POST /api/auth/send-friend-request`

**Açıklama:** Arkadaşlık isteği gönderir.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "to_user_id": "507f1f77bcf86cd799439012"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Arkadaşlık isteği gönderildi",
  "request_id": "507f1f77bcf86cd799439013"
}
```

### Arkadaşlık İsteğine Yanıt Verme

**Endpoint:** `POST /api/auth/respond-to-friend-request`

**Açıklama:** Gelen arkadaşlık isteğine yanıt verir.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "request_id": "507f1f77bcf86cd799439013",
  "action": "accept"  // "accept" veya "reject"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Arkadaşlık isteği kabul edildi"
}
```

### Arkadaşlık İsteklerini Getirme

**Endpoint:** `GET /api/auth/friend-requests`

**Açıklama:** Gelen arkadaşlık isteklerini getirir.

**Headers:** `Authorization: Bearer <token>`

**Başarılı Response:**
```json
{
  "status": "ok",
  "requests": [
    {
      "id": "507f1f77bcf86cd799439013",
      "from_user": {
        "id": "507f1f77bcf86cd799439012",
        "full_name": "Jane Doe",
        "avatar": "/media/avatars/avatar_456.jpg"
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

### Arkadaş Listesini Getirme

**Endpoint:** `GET /api/auth/friends`

**Açıklama:** Arkadaş listesini getirir.

**Headers:** `Authorization: Bearer <token>`

**Başarılı Response:**
```json
{
  "status": "ok",
  "friends": [
    {
      "id": "507f1f77bcf86cd799439012",
      "full_name": "Jane Doe",
      "avatar": "/media/avatars/avatar_456.jpg",
      "bio": "Frontend developer",
      "location": "Ankara, Turkey",
      "user_type": ["developer"],
      "reliability_score": 85
    }
  ],
  "count": 1
}
```

### Arkadaşı Kaldırma

**Endpoint:** `POST /api/auth/remove-friend`

**Açıklama:** Arkadaşı kaldırır.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "friend_id": "507f1f77bcf86cd799439012"
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Arkadaş kaldırıldı"
}
```

---

## Geliştirici Kayıt Sistemi (TC Kimlik + CV Analizi)

### TC Kimlik Kartı Doğrulama

**Endpoint:** `POST /api/auth/verify-id-card`

**Açıklama:** TC kimlik kartının ön yüzünü yükler ve Gemini AI ile analiz eder.

**Headers:** `Authorization: Bearer <token>`

**Body:** `multipart/form-data`
- `id_card_image`: Image file (JPEG, PNG, max 5MB)

**Başarılı Response:**
```json
{
  "name": "Ahmet",
  "surname": "Yılmaz",
  "tc": "12345678901",
  "birth_date": "1990-01-01",
  "issue_date": "2020-01-01",
  "expiry_date": "2030-01-01",
  "confidence": 0.95,
  "message": "Kimlik kartı başarıyla doğrulandı"
}
```

**Hatalı Response:**
```json
{
  "error": "Sadece kimlik fotoğrafı (.jpg, .jpeg, .png) yükleyin."
}
```

### CV Yükleme ve Analizi

**Endpoint:** `POST /api/auth/upload-cv`

**Açıklama:** CV dosyasını yükler, kimlikteki ad-soyad ile karşılaştırır ve Gemini AI ile analiz eder.

**Headers:** `Authorization: Bearer <token>`

**Body:** `multipart/form-data`
- `cv_file`: PDF file (max 10MB)

**Başarılı Response:**
```json
{
  "success": true,
  "message": "CV başarıyla doğrulandı ve analiz edildi.",
  "cv_name": "Ahmet Yılmaz",
  "id_name": "Ahmet Yılmaz",
  "languages_analysis": {
    "Python": "İleri Seviye",
    "JavaScript": "Orta Seviye",
    "React": "Orta Seviye",
    "Django": "İleri Seviye"
  },
  "known_languages": ["Python", "JavaScript", "React", "Django"],
  "language_levels": {
    "İleri Seviye": ["Python", "Django"],
    "Orta Seviye": ["JavaScript", "React"]
  }
}
```

**Hatalı Response (Kimlik doğrulaması yapılmamış):**
```json
{
  "error": "Önce kimlik doğrulaması yapmalısınız.",
  "debug": {
    "identity_verified": false,
    "verified_name": null,
    "verified_surname": null
  }
}
```

**Hatalı Response (Ad-soyad eşleşmiyor):**
```json
{
  "success": false,
  "error": "CV'deki ad-soyad kimlikle eşleşmiyor. Lütfen kendi CV'nizi yükleyin.",
  "cv_name": "Mehmet Demir",
  "id_name": "Ahmet Yılmaz"
}
```

### Geliştirici Kayıt Süreci

**Adım 1: Email Doğrulama**
```bash
POST /api/auth/send-verification-code
{
  "email": "developer@example.com"
}
```

**Adım 2: Email Doğrulama ve Kayıt**
```bash
POST /api/auth/verify-email-and-register
{
  "email": "developer@example.com",
  "verification_code": "123456",
  "full_name": "Ahmet Yılmaz",
  "password": "securepassword123",
  "user_type": ["developer"]
}
```

**Adım 3: TC Kimlik Kartı Doğrulama**
```bash
POST /api/auth/verify-id-card
Headers: Authorization: Bearer <token>
Body: multipart/form-data
- id_card_image: [TC kimlik kartı ön yüzü]
```

**Adım 4: CV Yükleme ve Analizi**
```bash
POST /api/auth/upload-cv
Headers: Authorization: Bearer <token>
Body: multipart/form-data
- cv_file: [CV PDF dosyası]
```

### Geliştirici Profil Bilgileri

**Endpoint:** `GET /api/auth/me`

**Headers:** `Authorization: Bearer <token>`

**Başarılı Response:**
```json
{
  "status": "ok",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "developer@example.com",
    "full_name": "Ahmet Yılmaz",
    "user_type": ["developer"],
    "identity_verified": true,
    "verified_name": "Ahmet",
    "verified_surname": "Yılmaz",
    "tc_verified": "12345678901",
    "cv_verified": true,
    "cv_name_detected": "Ahmet Yılmaz",
    "known_languages": ["Python", "JavaScript", "React", "Django"],
    "language_levels": {
      "İleri Seviye": ["Python", "Django"],
      "Orta Seviye": ["JavaScript", "React"]
    },
    "reliability_score": 85,
    "avatar": "/media/avatars/avatar_123.jpg"
  }
}
```

---