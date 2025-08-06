# BTK Backend - MongoDB Atlas Integration

Bu proje, BTK Hackathon 2025 için geliştirilmiş bir backend API'sidir. Django framework ve MongoDB veritabanı kullanılarak geliştirilmiştir.

## 🚀 Özellikler

- **MongoDB Atlas Integration**: Bulut tabanlı veritabanı
- **User Management**: Kullanıcı kayıt, giriş ve profil yönetimi
- **Project Management**: Proje oluşturma ve yönetimi
- **Idea Management**: Fikir paylaşımı ve yönetimi
- **Investment System**: Yatırım sistemi
- **Notification System**: Bildirim sistemi
- **Email Verification**: Email doğrulama sistemi
- **JWT Authentication**: Güvenli kimlik doğrulama
- **Gemini AI Integration**: AI destekli özellikler

## 🛠️ Teknolojiler

- **Django**: Web framework
- **MongoDB Atlas**: Bulut veritabanı
- **MongoEngine**: MongoDB ODM
- **JWT**: Kimlik doğrulama
- **Gemini AI**: AI entegrasyonu
- **Render**: Deployment platformu

## 📋 Kurulum

### Gereksinimler

- Python 3.8+
- MongoDB Atlas hesabı
- Gemini AI API key

### Adımlar

1. **Repository'yi klonlayın**:
   ```bash
   git clone https://github.com/your-username/btk-backend.git
   cd btk-backend
   ```

2. **Virtual environment oluşturun**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # veya
   venv\Scripts\activate  # Windows
   ```

3. **Bağımlılıkları yükleyin**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables ayarlayın**:
   ```bash
   # .env dosyası oluşturun
   MONGODB_HOST=mongodb+srv://username:password@cluster.mongodb.net/database
   GEMINI_API_KEY=your_gemini_api_key
   SECRET_KEY=your_django_secret_key
   ```

5. **Veritabanını test edin**:
   ```bash
   python test_atlas_connection.py
   ```

6. **Sunucuyu başlatın**:
   ```bash
   python manage.py runserver
   ```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Kullanıcı kaydı
- `POST /api/auth/login` - Kullanıcı girişi
- `POST /api/auth/verify-email` - Email doğrulama

### Users
- `GET /api/auth/me` - Kullanıcı profili
- `GET /api/auth/list` - Kullanıcı listesi
- `PUT /api/auth/me/edit` - Profil düzenleme

### Projects
- `GET /projects/` - Proje listesi
- `POST /projects/` - Proje oluşturma
- `GET /projects/<id>/` - Proje detayı

### Ideas
- `GET /ideas/` - Fikir listesi
- `POST /ideas/` - Fikir oluşturma
- `GET /ideas/<id>/` - Fikir detayı

## 🧪 Test

```bash
# Atlas bağlantısını test et
python test_atlas_connection.py

# Django testleri
python manage.py test
```

## 🚀 Deployment

Bu proje Render platformunda deploy edilmiştir. `render.yaml` dosyası deployment ayarlarını içerir.

## 📊 Veritabanı Şeması

### User Model
- `email`: String (unique)
- `password_hash`: String
- `full_name`: String
- `user_type`: List (developer, entrepreneur, investor, fikir_sahibi, admin)
- `github_verified`: Boolean
- `linkedin_verified`: Boolean
- `can_invest`: Boolean
- `created_at`: DateTime

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- **Email**: [your-email@example.com]
- **GitHub**: [@your-username]

## 🔄 Changelog

### v1.0.0
- MongoDB Atlas entegrasyonu
- User management sistemi
- Project ve Idea management
- JWT authentication
- Gemini AI entegrasyonu 