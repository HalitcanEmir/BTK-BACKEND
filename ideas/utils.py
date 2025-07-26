import google.generativeai as genai
import json
import re
from django.conf import settings

def clean_gemini_json(raw_text):
    """Gemini'den dönen cevaptaki kod bloğu işaretlerini temizle"""
    cleaned = re.sub(r"^```json|^```|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return cleaned

def analyze_project_with_gemini(project_description: str) -> dict:
    """Proje açıklamasını Gemini ile analiz et"""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Aşağıda bir yazılım projesi fikri yer alıyor. Lütfen analiz et ve aşağıdaki sorulara net cevaplar ver:

1. Bu projede hangi teknolojiler kullanılmalıdır? (Backend, frontend, veri tabanı, varsa AI kütüphaneleri)
2. Bu projeyi geliştirecek kişilerin yazılım bilgi seviyesi ne olmalı? (Başlangıç, Orta, İleri)
3. Kaç kişilik bir ekip önerirsiniz? Hangi rollerle?
4. Projenin tahmini tamamlanma süresi nedir? (gün/hafta olarak tahmin)
5. Ek olarak bu projeyi geliştirirken dikkat edilmesi gereken kritik noktalar varsa belirtin.

Proje açıklaması:
{project_description}

Sadece JSON formatında döndür:
{{
  "technologies": ["Python", "FastAPI", "React", "PostgreSQL", "OpenAI API"],
  "skill_level": "Orta",
  "team_size": 3,
  "roles": ["Backend Developer", "Frontend Developer", "AI/ML Researcher"],
  "estimated_duration": "2-3 hafta",
  "notes": "AI kısmı için veri temizliği kritik. API limiti göz önüne alınmalı."
}}

Sadece JSON döndür, başka açıklama ekleme."""
        
        response = model.generate_content(prompt)
        
        if not response.text or response.text.strip() == "":
            return {"error": "Gemini boş cevap döndü"}
        
        try:
            cleaned_text = clean_gemini_json(response.text)
            data = json.loads(cleaned_text)
            return data
        except json.JSONDecodeError:
            return {"error": f"Gemini JSON döndürmedi, raw cevap: {response.text[:200]}"}
            
    except Exception as e:
        return {"error": f"Gemini API hatası: {str(e)}"} 