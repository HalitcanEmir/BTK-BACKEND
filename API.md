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