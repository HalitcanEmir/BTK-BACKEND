# Proje Başvuru Sistemi - Günlük Çalışma Saati Özelliği

## 🎯 Amaç

Bu özellik, projeye başvuru yapan geliştiricilerden sadece "teknoloji bilgisi" değil, **günde kaç saat çalışabileceği** bilgisini de almak için geliştirilmiştir. Bu bilgi, Gemini AI'ın görevlendirme ve proje süresi tahmini yaparken kullanılacaktır.

## 🏗️ Sistem Mimarisi

### Veritabanı Yapısı

**JoinRequest Modeli** (`ideas/models.py`):
```python
class JoinRequest(Document):
    idea = ReferenceField(Idea, required=False)
    project = ReferenceField('Project', required=False)
    user = ReferenceField(User, required=True)
    message = StringField()
    daily_available_hours = IntField(min_value=1, max_value=12)  # YENİ ALAN
    status = StringField(default='pending')
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    approved_by = ReferenceField(User)
    approved_at = DateTimeField()
```

### Yeni Alan Özellikleri

- **Alan Adı:** `daily_available_hours`
- **Veri Tipi:** `IntField`
- **Sınırlar:** 1-12 saat arası
- **Zorunlu:** Evet
- **Benzersiz:** Hayır (kullanıcı farklı projelere farklı saatlerde başvurabilir)

## 📝 API Endpoint'leri

### 1. Projeye Başvuru Yapma
```
POST /projects/{id}/join-request
```

**Gerekli Alanlar:**
```json
{
  "daily_available_hours": 4,
  "message": "Bu projede frontend geliştirme yapmak istiyorum."
}
```

**Başarılı Response:**
```json
{
  "status": "ok",
  "message": "Proje başvurunuz alındı",
  "request_id": "665f1c2e8b3e2a1a2b3c4d5e"
}
```

### 2. Başvuru Durumu Kontrolü
```
GET /projects/{id}/join-request/status
```

**Response:**
```json
{
  "has_applied": true,
  "status": "pending",
  "message": "Bu projede frontend geliştirme yapmak istiyorum.",
  "daily_available_hours": 4
}
```

### 3. Admin - Başvuru Listesi
```
GET /projects/admin/join-requests
```

**Response:**
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

### 4. Gemini AI - Ekip Planlaması Verisi
```
GET /projects/{id}/team-planning-data
```

**Response:**
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

## 🔒 Güvenlik ve Validasyon

### Validasyon Kuralları

1. **Zorunlu Alan:** `daily_available_hours` belirtilmelidir
2. **Sayısal Değer:** Sadece sayı kabul edilir
3. **Sınırlar:** 1-12 saat arası olmalıdır
4. **Benzersiz Başvuru:** Aynı kullanıcı aynı projeye birden fazla başvuru yapamaz

### Hata Mesajları

```json
{
  "status": "error",
  "message": "Günlük çalışma saati belirtmelisiniz"
}
```

```json
{
  "status": "error", 
  "message": "Günlük çalışma saati sayı olmalıdır"
}
```

```json
{
  "status": "error",
  "message": "Günlük çalışma saati 1-12 saat arasında olmalıdır"
}
```

## 🤖 Gemini AI Entegrasyonu

### Kullanım Senaryosu

1. **Proje Ekibi Oluşturulduğunda:**
   - Sistem tüm onaylanmış başvuruları çeker
   - Her kullanıcının `daily_available_hours` değeri okunur
   - Gemini'ye gönderilecek prompt içinde bu saatler yer alır

2. **Gemini Prompt Örneği:**
```
Proje: E-Ticaret Platformu
Ekip Üyeleri:
- Ahmet Yılmaz: 4 saat/gün
- Ayşe Demir: 6 saat/gün
- Mehmet Kaya: 3 saat/gün

Bu ekip üyelerinin günlük çalışma saatlerine göre görev dağılımı yapın.
```

### Veri Yapısı

Gemini'ye gönderilen veri şu formatta olacak:
```json
{
  "project_title": "E-Ticaret Platformu",
  "team_members": [
    {
      "user_name": "Ahmet Yılmaz",
      "daily_available_hours": 4,
      "message": "Frontend geliştirme yapmak istiyorum"
    }
  ],
  "total_daily_hours": 4
}
```

## 🔄 Diğer Modüllerle Entegrasyon

### 1. Görev Planlama Sistemi
- Bu değer olmadan görev dağılımı yapılamaz
- Her kullanıcının kapasitesine göre görev atanır

### 2. Takvim Sistemi
- Bu saatlere göre hangi günlerde ne yapılacağı belirlenebilir
- Proje süresi tahmini yapılabilir

### 3. Performans Puanı
- Ne kadar süre ayırdığı ve bunu kullanıp kullanmadığı karşılaştırılabilir
- Verimlilik analizi yapılabilir

## 📋 Test Senaryosu

Test dosyası: `test_project_application.py`

```bash
python test_project_application.py
```

Bu dosya şunları test eder:
- Başvuru yapma
- Validasyon kuralları
- Admin işlemleri
- Gemini AI entegrasyonu

## 🚀 Kullanım Adımları

### Frontend Geliştirici İçin

1. **Başvuru Formu:**
```javascript
const applicationData = {
  daily_available_hours: 4,  // Zorunlu
  message: "Bu projede frontend geliştirme yapmak istiyorum."
};

fetch(`/projects/${projectId}/join-request`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(applicationData)
});
```

2. **Başvuru Durumu Kontrolü:**
```javascript
fetch(`/projects/${projectId}/join-request/status`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Admin İçin

1. **Başvuru Listesi:**
```javascript
fetch('/projects/admin/join-requests?status=pending');
```

2. **Başvuru Onaylama:**
```javascript
fetch(`/projects/admin/join-requests/${requestId}/approve`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});
```

## 📊 Veri Akışı

```
Kullanıcı Başvurusu
    ↓
daily_available_hours + message
    ↓
Veritabanına Kayıt
    ↓
Admin Onayı
    ↓
Ekip Üyeliği
    ↓
Gemini AI Planlaması
    ↓
Görev Dağılımı
```

## ✅ Özet

Bu özellik sayesinde:

✅ **Kullanıcı:** Günde kaç saat çalışabileceğini belirtir  
✅ **Backend:** Bu veriyi başvuruya ekleyerek veritabanına kaydeder  
✅ **Admin:** Başvuruları günlük çalışma saatleriyle birlikte görür  
✅ **Gemini AI:** Görev planlamasında bu bilgileri kullanır  
✅ **Entegrasyon:** Görev, performans, proje ilerleyişi modülleriyle entegre çalışır  

Bu sistem, proje yönetimini daha verimli ve gerçekçi hale getirir. 