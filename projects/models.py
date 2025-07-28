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
    
    meta = {
        'indexes': [
            {'fields': ['project', 'assigned_user']},
            {'fields': ['assigned_user', 'status']},
            {'fields': ['end_date', 'status']}
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
