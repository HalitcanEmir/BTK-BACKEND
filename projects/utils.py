import google.generativeai as genai
from django.conf import settings
import json

# Gemini AI'yı yapılandır
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_ai_response(prompt, context=None):
    """
    Gemini AI'dan yanıt alır
    
    Args:
        prompt (str): AI'ya gönderilecek soru/prompt
        context (dict): Ek bağlam bilgileri
    
    Returns:
        dict: AI yanıtı ve durum bilgisi
    """
    try:
        # Model seç
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Bağlam varsa prompt'a ekle
        if context:
            full_prompt = f"""
            Bağlam: {json.dumps(context, ensure_ascii=False)}
            
            Soru: {prompt}
            
            Lütfen Türkçe yanıt ver.
            """
        else:
            full_prompt = prompt
        
        # AI'dan yanıt al
        response = model.generate_content(full_prompt)
        
        return {
            'status': 'success',
            'response': response.text,
            'model': 'gemini-1.5-flash'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'AI yanıtı alınamadı'
        }

def analyze_project(project_data):
    """
    Proje verilerini analiz eder ve AI önerileri sunar
    
    Args:
        project_data (dict): Proje bilgileri
    
    Returns:
        dict: AI analizi ve önerileri
    """
    prompt = f"""
    Bu proje hakkında analiz yap ve öneriler sun:
    
    Proje Adı: {project_data.get('title', 'Bilinmiyor')}
    Açıklama: {project_data.get('description', 'Yok')}
    Kategori: {project_data.get('category', 'Bilinmiyor')}
    Takım Büyüklüğü: {project_data.get('team_size', 0)}
    Hedef Miktar: {project_data.get('target_amount', 0)}
    Mevcut Miktar: {project_data.get('current_amount', 0)}
    Beğeni Sayısı: {project_data.get('like_count', 0)}
    
    Lütfen şunları analiz et:
    1. Projenin güçlü yanları
    2. Geliştirilebilecek alanlar
    3. Yatırımcılar için öneriler
    4. Geliştiriciler için öneriler
    5. Genel değerlendirme (1-10 arası)
    
    Yanıtı JSON formatında ver.
    """
    
    return get_ai_response(prompt, project_data)

def generate_project_suggestions(user_profile):
    """
    Kullanıcı profiline göre proje önerileri üretir
    
    Args:
        user_profile (dict): Kullanıcı profili
    
    Returns:
        dict: AI önerileri
    """
    prompt = f"""
    Bu kullanıcı için proje önerileri üret:
    
    Kullanıcı Tipi: {user_profile.get('user_type', [])}
    Beceriler: {user_profile.get('skills', [])}
    İlgi Alanları: {user_profile.get('interests', [])}
    
    Lütfen şunları öner:
    1. Geliştirebileceği proje fikirleri
    2. İşbirliği yapabileceği alanlar
    3. Öğrenmesi gereken teknolojiler
    4. Kariyer gelişimi için öneriler
    
    Yanıtı JSON formatında ver.
    """
    
    return get_ai_response(prompt, user_profile)

def get_investment_advice(project_data, investor_profile):
    """
    Yatırım tavsiyesi üretir
    
    Args:
        project_data (dict): Proje bilgileri
        investor_profile (dict): Yatırımcı profili
    
    Returns:
        dict: Yatırım tavsiyesi
    """
    prompt = f"""
    Bu proje için yatırım tavsiyesi ver:
    
    Proje Bilgileri:
    - Adı: {project_data.get('title', 'Bilinmiyor')}
    - Açıklama: {project_data.get('description', 'Yok')}
    - Hedef Miktar: {project_data.get('target_amount', 0)}
    - Mevcut Miktar: {project_data.get('current_amount', 0)}
    - Beğeni Sayısı: {project_data.get('like_count', 0)}
    
    Yatırımcı Profili:
    - Deneyim: {investor_profile.get('experience', 'Bilinmiyor')}
    - Risk Toleransı: {investor_profile.get('risk_tolerance', 'Orta')}
    - Yatırım Miktarı: {investor_profile.get('investment_amount', 0)}
    
    Lütfen şunları değerlendir:
    1. Yatırım riski (Düşük/Orta/Yüksek)
    2. Önerilen yatırım miktarı
    3. Beklenen getiri oranı
    4. Yatırım süresi önerisi
    5. Risk faktörleri
    6. Genel tavsiye (Yatır/Yatırma)
    
    Yanıtı JSON formatında ver.
    """
    
    context = {
        'project': project_data,
        'investor': investor_profile
    }
    
    return get_ai_response(prompt, context) 