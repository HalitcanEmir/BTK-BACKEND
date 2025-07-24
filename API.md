# BTK Backend API Dökümantasyonu

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
``` 