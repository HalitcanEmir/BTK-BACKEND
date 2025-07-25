import base64
import os

def image_to_base64(image_path):
    """Görsel dosyasını base64 formatına çevirir"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        # Gemini'nin beklediği format için "data:image/jpeg;base64," önekini ekle
        return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Hata: {e}")
        return None

# Kimlik görseli dosya adı
image_file_path = "WhatsApp Görsel 2025-07-26 saat 01.49.55_954f4fd4.jpg"

# Dosya var mı kontrol et
if os.path.exists(image_file_path):
    base64_image_data = image_to_base64(image_file_path)
    if base64_image_data:
        print("✅ Base64 dönüşümü başarılı!")
        print(f"📁 Dosya: {image_file_path}")
        print(f"📏 Base64 uzunluğu: {len(base64_image_data)} karakter")
        print("\n📋 Postman için kullan:")
        print(f'{{"id_card_image": "{base64_image_data[:100]}...", "linkedin_url": "https://www.linkedin.com/in/halitcanemir/"}}')
    else:
        print("❌ Base64 dönüşümü başarısız!")
else:
    print(f"❌ Dosya bulunamadı: {image_file_path}")
    print("📁 Mevcut dosyalar:")
    for file in os.listdir('.'):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"  - {file}") 