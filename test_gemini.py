import google.generativeai as genai
from django.conf import settings
import base64
import json

# Gemini AI'yı yapılandır
genai.configure(api_key='AIzaSyCbCKfQbDi8_qsBNMcaFBly8RppdrV791Q')

def test_gemini_with_image():
    """Gemini AI ile kimlik kartı testi"""
    try:
        print("🔍 Gemini AI test başlatılıyor...")
        
        # Dosyayı oku
        with open('WhatsApp Görsel 2025-07-26 saat 01.49.55_863fce7f.jpg', 'rb') as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"✅ Dosya okundu, boyut: {len(image_bytes)} bytes")
        print(f"✅ Base64 uzunluk: {len(image_base64)} karakter")
        
        # Model seç
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Bu bir kimliğin ön yüzü. Lütfen sadece adı ve soyadı bilgilerini çıkar ve JSON formatında döndür.
        Eğer metin okunamıyorsa 'null' döndür.
        
        Yanıt formatı:
        {
          "name": "Ad",
          "surname": "Soyad"
        }
        """
        
        # Görseli AI'ya gönder
        image_data = {"mime_type": "image/jpeg", "data": image_base64}
        
        print("🤖 Gemini AI'ya gönderiliyor...")
        response = model.generate_content([prompt, image_data])
        
        print(f"📥 AI yanıtı alındı: {response.text}")
        
        # JSON parse et
        try:
            result = json.loads(response.text)
            print(f"✅ JSON parse başarılı: {result}")
            return result
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse hatası: {e}")
            print(f"📄 Raw response: {response.text}")
            return None
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return None

if __name__ == "__main__":
    test_gemini_with_image() 