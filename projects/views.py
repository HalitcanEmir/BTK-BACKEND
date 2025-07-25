from django.shortcuts import render
from django.http import JsonResponse
from .models import Project
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# Geliştirilen Projeler Sayfası
# GET /api/projects/
# Açıklama: Tüm projeleri listeler
def projects_list(request):
    return JsonResponse({"message": "Geliştirilen Projeler Sayfası"})

# Proje Detay Sayfası
# GET /api/projects/<id>
# Açıklama: Belirli bir projenin detayını getirir
def project_detail(request, id):
    return JsonResponse({"message": f"Proje Detay Sayfası: {id}"})

# Geliştirici Bulma / İlan Listesi
# GET /api/projects/jobs
# Açıklama: Geliştirici ilanlarını listeler
def jobs_list(request):
    return JsonResponse({"message": "Geliştirici İlan Listesi"})

# Geliştirici İlan Detay Sayfası
# GET /api/projects/jobs/<id>
# Açıklama: Geliştirici ilan detayını getirir
def job_detail(request, id):
    return JsonResponse({"message": f"Geliştirici İlan Detay Sayfası: {id}"})

# Proje Ekip Paneli ve alt fonksiyonlar
# GET /api/projects/<id>/team
# Açıklama: Proje ekibini ve başvuranları gösterir
def project_team(request, id):
    return JsonResponse({"message": f"Proje Ekip Paneli: {id}"})

# POST /api/projects/<id>/team/approve
# Açıklama: Aday onaylama işlemi
def approve_candidate(request, id):
    return JsonResponse({"message": f"Aday Onaylama: {id}"})

# POST /api/projects/<id>/team/reject
# Açıklama: Aday reddetme işlemi
def reject_candidate(request, id):
    return JsonResponse({"message": f"Aday Reddetme: {id}"})

# Proje Planlama
# GET /api/projects/<id>/plan
# Açıklama: Proje planı ve yol haritası
def project_plan(request, id):
    return JsonResponse({"message": f"Proje Planlama: {id}"})

# Görev Dağılımı
# GET /api/projects/<id>/tasks
# Açıklama: Proje görev dağılımı
def project_tasks(request, id):
    return JsonResponse({"message": f"Görev Dağılımı: {id}"})

# Takım İçi Mesajlaşma
# GET /api/projects/<id>/chat
# Açıklama: Takım içi mesajlaşma paneli
def project_chat(request, id):
    return JsonResponse({"message": f"Takım İçi Mesajlaşma: {id}"})

# AI Yardımcıları Paneli
# GET /api/projects/<id>/ai
# Açıklama: AI yardımcıları paneli
def project_ai_panel(request, id):
    return JsonResponse({"message": f"AI Yardımcıları Paneli: {id}"})

@csrf_exempt
def completed_projects_list(request):
    completed = request.GET.get('completed')
    if completed == 'true':
        projects = Project.objects(is_completed=True)
    else:
        projects = Project.objects()
    data = []
    for project in projects:
        data.append({
            'id': str(project.id),
            'title': getattr(project, 'title', None),
            'description': getattr(project, 'description', None),
            'team': getattr(project, 'team', []),  # varsa
            'completed_at': project.completed_at.isoformat() if project.completed_at else None,
            'success_label': getattr(project, 'success_label', None),
            'cover_image': getattr(project, 'cover_image', None),  # opsiyonel
            'story': getattr(project, 'story', None),  # opsiyonel
        })
    return JsonResponse({'projects': data})
