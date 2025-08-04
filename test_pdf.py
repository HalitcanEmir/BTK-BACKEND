#!/usr/bin/env python3
"""
PDF Test Script
Sadece PDF okuma fonksiyonunu test eder
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.utils import extract_text_from_pdf, detect_name_from_cv, compare_names

def test_pdf_functions():
    """PDF fonksiyonlarını test et"""
    print("🧪 PDF fonksiyonları test ediliyor...")
    
    # Test 1: Import kontrolü
    try:
        import PyPDF2
        print("✅ PyPDF2 import başarılı")
    except ImportError as e:
        print(f"❌ PyPDF2 import hatası: {e}")
        return False
    
    try:
        import fitz
        print("✅ PyMuPDF import başarılı")
    except ImportError as e:
        print(f"❌ PyMuPDF import hatası: {e}")
        return False
    
    # Test 2: Fonksiyon varlığı
    if hasattr(extract_text_from_pdf, '__call__'):
        print("✅ extract_text_from_pdf fonksiyonu mevcut")
    else:
        print("❌ extract_text_from_pdf fonksiyonu bulunamadı")
        return False
    
    if hasattr(detect_name_from_cv, '__call__'):
        print("✅ detect_name_from_cv fonksiyonu mevcut")
    else:
        print("❌ detect_name_from_cv fonksiyonu bulunamadı")
        return False
    
    if hasattr(compare_names, '__call__'):
        print("✅ compare_names fonksiyonu mevcut")
    else:
        print("❌ compare_names fonksiyonu bulunamadı")
        return False
    
    print("✅ Tüm PDF fonksiyonları hazır!")
    return True

if __name__ == "__main__":
    success = test_pdf_functions()
    if success:
        print("🎉 PDF test başarılı!")
        sys.exit(0)
    else:
        print("💥 PDF test başarısız!")
        sys.exit(1) 