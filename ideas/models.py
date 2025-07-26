from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField, BooleanField, FloatField, ListField
import datetime
from users.models import User

# Fikir modeli
class Idea(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    category = StringField()
    problem = StringField()
    solution = StringField()
    estimated_cost = FloatField()
    owner_id = ReferenceField(User)
    created_by = ReferenceField(User)
    approved_by = ReferenceField(User)
    license_accepted = BooleanField(default=False)
    license_accepted_at = DateTimeField()
    owner_share_percent = IntField(default=10)
    status = StringField(default='pending_admin_approval')  # pending_admin_approval, approved, rejected
    created_at = DateTimeField()
    updated_at = DateTimeField()
    approved_at = DateTimeField()  # Eski veritabanı uyumluluğu için
    rejected_at = DateTimeField()  # Eski veritabanı uyumluluğu için
    rejected_by = ReferenceField(User)  # Eski veritabanı uyumluluğu için
    rejection_reason = StringField()  # Eski veritabanı uyumluluğu için
    likes = IntField(default=0)
    dislikes = IntField(default=0)
    passes = IntField(default=0)
    swipe_score = FloatField(default=0.0)

class SwipeVote(Document):
    idea = ReferenceField(Idea, required=True)
    user = ReferenceField(User, required=True)
    vote = StringField(required=True)  # like, dislike, pass
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    meta = {
        'indexes': [
            {'fields': ['idea', 'user'], 'unique': True}
        ]
    }

class JoinRequest(Document):
    idea = ReferenceField(Idea, required=False)  # Fikir başvurusu için
    project = ReferenceField('Project', required=False)  # Proje başvurusu için
    user = ReferenceField(User, required=True)
    message = StringField()
    status = StringField(default='pending')  # pending, approved, rejected
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    approved_by = ReferenceField(User)
    approved_at = DateTimeField()
    meta = {
        'indexes': [
            {'fields': ['idea', 'user'], 'unique': True},
            {'fields': ['project', 'user'], 'unique': True}
        ]
    }

class ProjectMessage(Document):
    idea = ReferenceField(Idea, required=False)  # Fikir sohbeti için
    project = ReferenceField('Project', required=False)  # Proje sohbeti için
    user = ReferenceField(User, required=True)
    content = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)

class ProjectAnalysis(Document):
    """Gemini AI ile yapılan proje analizi sonuçları"""
    idea = ReferenceField('Idea', required=True)
    technologies = ListField(StringField())  # Kullanılacak teknolojiler
    skill_level = StringField()  # Başlangıç/Orta/İleri
    team_size = IntField()  # Kaç kişilik ekip
    roles = ListField(StringField())  # Ekip rolleri
    estimated_duration = StringField()  # Tahmini süre
    notes = StringField()  # Ek notlar (TextField yerine StringField)
    created_at = DateTimeField()
