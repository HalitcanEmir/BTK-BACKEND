from PIL import Image, ImageDraw
import os

# Test kimlik kartı oluştur
img = Image.new('RGB', (400, 250), 'white')
draw = ImageDraw.Draw(img)

# Kimlik bilgileri
draw.text((50, 30), "TURKIYE CUMHURIYETI KIMLIK KARTI", fill='black')
draw.text((50, 60), "T.C. KIMLIK NO:", fill='black')
draw.text((50, 80), "12020925966", fill='black')
draw.text((50, 110), "ADI:", fill='black')
draw.text((50, 130), "HALITCAN", fill='black')
draw.text((50, 160), "SOYADI:", fill='black')
draw.text((50, 180), "EMIR", fill='black')

# Kaydet
img.save('test_id_card.jpg')
print("✅ Test kimlik kartı oluşturuldu: test_id_card.jpg")
print("📁 Dosya yolu:", os.path.abspath('test_id_card.jpg')) 