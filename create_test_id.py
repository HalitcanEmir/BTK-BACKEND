from PIL import Image, ImageDraw, ImageFont
import os

def create_test_id_card():
    """Test kimlik kartı oluşturur"""
    try:
        # Yeni görsel oluştur
        img = Image.new('RGB', (400, 250), color='white')
        draw = ImageDraw.Draw(img)
        
        # Basit font (varsayılan)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Kimlik kartı bilgileri
        draw.text((50, 30), "TÜRKİYE CUMHURİYETİ KİMLİK KARTI", fill='black', font=font)
        draw.text((50, 60), "T.C. KIMLIK NO:", fill='black', font=font)
        draw.text((50, 80), "12020925966", fill='black', font=font)
        draw.text((50, 110), "ADI:", fill='black', font=font)
        draw.text((50, 130), "HALITCAN", fill='black', font=font)
        draw.text((50, 160), "SOYADI:", fill='black', font=font)
        draw.text((50, 180), "EMİR", fill='black', font=font)
        draw.text((50, 210), "DOĞUM TARİHİ: 25.03.2007", fill='black', font=font)
        
        # Dosyayı kaydet
        filename = "test_id_card.jpg"
        img.save(filename)
        
        print(f"✅ Test kimlik kartı oluşturuldu: {filename}")
        print(f"📁 Dosya yolu: {os.path.abspath(filename)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Test kimlik kartı oluşturulamadı: {e}")
        return None

if __name__ == "__main__":
    create_test_id_card() 