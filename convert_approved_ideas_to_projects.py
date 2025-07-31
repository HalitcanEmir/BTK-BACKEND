#!/usr/bin/env python
"""
Bu script onaylanmış fikirleri projelere dönüştürür.
Kullanım: python convert_approved_ideas_to_projects.py
"""

import os
import sys
import django
from datetime import datetime

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ideas.models import Idea
from projects.models import Project
from bson import ObjectId

def convert_approved_ideas_to_projects():
    """Onaylanmış fikirleri projelere dönüştürür"""
    
    # Onaylanmış fikirleri bul
    approved_ideas = Idea.objects(status='approved')
    print(f"Toplam {approved_ideas.count()} onaylanmış fikir bulundu.")
    
    converted_count = 0
    skipped_count = 0
    
    for idea in approved_ideas:
        # Bu fikir için zaten proje var mı kontrol et
        existing_project = Project.objects(title=idea.title, project_owner=idea.owner_id).first()
        
        if existing_project:
            print(f"Fikir '{idea.title}' için zaten proje mevcut. Atlanıyor.")
            skipped_count += 1
            continue
        
        try:
            # Yeni proje oluştur
            project = Project(
                title=idea.title,
                description=idea.description,
                category=idea.category,
                created_at=idea.approved_at or idea.created_at,
                is_approved=True,
                is_completed=False,
                project_owner=idea.owner_id,
                status='active',
                target_amount=idea.estimated_cost or 0,
                current_amount=0
            )
            project.save()
            
            print(f"✓ Fikir '{idea.title}' projeye dönüştürüldü. Proje ID: {project.id}")
            converted_count += 1
            
        except Exception as e:
            print(f"✗ Fikir '{idea.title}' dönüştürülürken hata: {e}")
    
    print(f"\nÖzet:")
    print(f"- Dönüştürülen fikir sayısı: {converted_count}")
    print(f"- Atlanan fikir sayısı: {skipped_count}")
    print(f"- Toplam işlenen fikir: {converted_count + skipped_count}")

def list_all_projects():
    """Tüm projeleri listeler"""
    projects = Project.objects.all()
    print(f"\nToplam {projects.count()} proje mevcut:")
    
    for project in projects:
        print(f"- ID: {project.id}")
        print(f"  Başlık: {project.title}")
        print(f"  Durum: {project.status}")
        print(f"  Tamamlandı: {project.is_completed}")
        print(f"  Sahip: {project.project_owner.full_name if project.project_owner else 'Bilinmiyor'}")
        print()

if __name__ == "__main__":
    print("Onaylanmış fikirleri projelere dönüştürme işlemi başlıyor...")
    
    # Önce mevcut projeleri listele
    list_all_projects()
    
    # Dönüştürme işlemini yap
    convert_approved_ideas_to_projects()
    
    # Sonra tekrar projeleri listele
    print("\nDönüştürme işlemi tamamlandı. Güncel proje listesi:")
    list_all_projects() 