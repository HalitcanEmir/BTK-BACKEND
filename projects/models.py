from django.db import models
from mongoengine import Document, BooleanField, DateTimeField, StringField, ListField, ReferenceField, EmbeddedDocumentField, EmbeddedDocument, IntField, FloatField
import datetime

# Create your models here.

class ProjectCompletionRequest(EmbeddedDocument):
    requester = ReferenceField('User', required=True)
    requested_at = DateTimeField(required=True)
    status = StringField(default='pending', choices=['pending', 'approved', 'rejected'])
    admin_response = StringField()
    responded_at = DateTimeField()
    admin_user = ReferenceField('User')

class InvestmentOffer(EmbeddedDocument):
    investor = ReferenceField('User', required=True)
    amount = FloatField(required=True)
    description = StringField()
    offered_at = DateTimeField(required=True)
    status = StringField(default='pending', choices=['pending', 'approved', 'rejected'])
    responded_at = DateTimeField()
    response_note = StringField()

class ProjectLike(EmbeddedDocument):
    user = ReferenceField('User', required=True)
    liked_at = DateTimeField(required=True)

class ProjectTask(Document):
    """Proje görevleri"""
    project = ReferenceField('Project', required=True)
    title = StringField(required=True)
    description = StringField()
    assigned_user = ReferenceField('User', required=True)
    assigned_by = ReferenceField('User', required=True)  # Görevi atayan admin
    start_date = DateTimeField(required=True)
    end_date = DateTimeField(required=True)
    duration_days = IntField(required=True)
    status = StringField(default='to-do', choices=['to-do', 'in-progress', 'done', 'cancelled'])
    priority = StringField(default='medium', choices=['low', 'medium', 'high', 'urgent'])
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    completed_at = DateTimeField()
    completion_notes = StringField()
    
    # Yeni alanlar - görev takibi için
    is_overdue = BooleanField(default=False)
    delay_days = IntField(default=0)
    on_time = BooleanField(default=True)
    progress_percentage = IntField(default=0, min_value=0, max_value=100)
    estimated_hours = IntField()  # Tahmini çalışma saati
    actual_hours = IntField(default=0)  # Gerçek çalışma saati
    user_notes = StringField()  # Kullanıcının notları
    admin_notes = StringField()  # Admin notları
    
    meta = {
        'indexes': [
            {'fields': ['project', 'assigned_user']},
            {'fields': ['assigned_user', 'status']},
            {'fields': ['end_date', 'status']},
            {'fields': ['is_overdue', 'status']},
            {'fields': ['assigned_user', 'is_overdue']}
        ]
    }

class TaskLog(Document):
    """Görev logları - başlama, bitirme, gecikme vs."""
    task = ReferenceField(ProjectTask, required=True)
    user = ReferenceField('User', required=True)
    action = StringField(required=True, choices=['started', 'completed', 'paused', 'resumed', 'delayed', 'updated'])
    notes = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'indexes': [
            {'fields': ['task', 'created_at']},
            {'fields': ['user', 'created_at']}
        ]
    }

class ProjectTimeline(Document):
    """Proje timeline analizi"""
    project = ReferenceField('Project', required=True)
    mvp_deadline = DateTimeField(required=True)
    full_project_deadline = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ReferenceField('User', required=True)
    
    # Analiz sonuçları
    total_tasks = IntField(default=0)
    completed_tasks = IntField(default=0)
    pending_tasks = IntField(default=0)
    risk_level = StringField(choices=['low', 'medium', 'high', 'critical'], default='low')
    
    meta = {
        'indexes': [
            {'fields': ['project']},
            {'fields': ['mvp_deadline']},
            {'fields': ['full_project_deadline']}
        ]
    }

class ProjectMilestone(Document):
    """Proje milestone'ları"""
    timeline = ReferenceField(ProjectTimeline, required=True)
    date = DateTimeField(required=True)
    description = StringField(required=True)
    milestone_type = StringField(choices=['mvp', 'development', 'testing', 'deployment', 'launch'], default='development')
    status = StringField(choices=['pending', 'completed', 'delayed'], default='pending')
    completed_at = DateTimeField()
    
    meta = {
        'indexes': [
            {'fields': ['timeline', 'date']},
            {'fields': ['status']}
        ]
    }

class ProjectRisk(Document):
    """Proje risk analizi"""
    timeline = ReferenceField(ProjectTimeline, required=True)
    task_title = StringField(required=True)
    reason = StringField(required=True)
    risk_level = StringField(choices=['low', 'medium', 'high', 'critical'], default='medium')
    mitigation_strategy = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'indexes': [
            {'fields': ['timeline', 'risk_level']}
        ]
    }

class Project(Document):
    title = StringField(required=True)
    description = StringField()
    category = StringField()
    created_at = DateTimeField()
    is_completed = BooleanField(default=False)
    completed_at = DateTimeField()
    success_label = StringField()
    is_approved = BooleanField(default=False)
    supporters = ListField(ReferenceField('User'))
    team_members = ListField(ReferenceField('User'))
    completion_requests = ListField(EmbeddedDocumentField(ProjectCompletionRequest))
    investment_offers = ListField(EmbeddedDocumentField(InvestmentOffer))
    likes = ListField(EmbeddedDocumentField(ProjectLike))
    # Yeni alanlar
    target_amount = FloatField(default=0)
    current_amount = FloatField(default=0)
    project_owner = ReferenceField('User')
    status = StringField(default='active', choices=['active', 'completed', 'cancelled'])
    live_stream_url = StringField()
    share_url = StringField()
