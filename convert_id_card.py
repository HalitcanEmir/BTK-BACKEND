import base64
import os

def image_to_base64(image_path):
    """Kimlik kartı görselini base64 formatına çevirir"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Hata: {e}")
        return None

# Kimlik kartı dosya adı
image_file_path = "WhatsApp Görsel 2025-07-26 saat 01.49.55_863fce7f.jpg"

print("🔍 Kimlik kartı dosyası aranıyor...")
print(f"📁 Aranan dosya: {image_file_path}")

# Dosya var mı kontrol et
if os.path.exists(image_file_path):
    print("✅ Dosya bulundu!")
    base64_image_data = image_to_base64(image_file_path)
    if base64_image_data:
        print("✅ Base64 dönüşümü başarılı!")
        print(f"📏 Base64 uzunluğu: {len(base64_image_data)} karakter")
        print("\n📋 Postman için kopyala:")
        print("=" * 50)
        print(f'{{"id_card_image": "{base64_image_data}", "linkedin_url": "https://www.linkedin.com/in/halitcanemir/"}}')
        print("=" * 50)
    else:
        print("❌ Base64 dönüşümü başarısız!")
else:
    print(f"❌ Dosya bulunamadı: {image_file_path}")
    print("\n📁 Mevcut dosyalar:")
    for file in os.listdir('.'):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"  - {file}")
    
    print("\n💡 Çözümler:")
    print("1. Kimlik görselini bu klasöre kopyala")
    print("2. Dosya adını düzelt")
    print("3. Tam yolu kullan") 