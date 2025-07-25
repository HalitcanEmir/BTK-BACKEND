from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField, BooleanField, FloatField, ListField
import datetime
from users.models import User

# Fikir modeli
class Idea(Document):
    title = StringField(required=True)
    description = StringField()
    category = StringField()
    problem = StringField()
    solution = StringField()
    estimated_cost = IntField()
    owner_id = ReferenceField(User, required=True)
    created_by = ReferenceField(User, required=True)
    license_accepted = BooleanField(required=True)
    license_accepted_at = DateTimeField()
    owner_share_percent = IntField(default=10)
    status = StringField(default='pending_admin_approval', choices=['pending', 'approved', 'rejected', 'pending_admin_approval'])
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    approved_at = DateTimeField()
    approved_by = ReferenceField(User)
    rejected_at = DateTimeField()
    rejected_by = ReferenceField(User)
    rejection_reason = StringField()
    likes = IntField(default=0)
    dislikes = IntField(default=0)
    passes = IntField(default=0)
    swipe_score = FloatField(default=0.0)

class SwipeVote(Document):
    idea = ReferenceField(Idea, required=True)
    user = ReferenceField('User', required=True)
    vote = StringField(choices=["like", "dislike", "pass"], required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    meta = {
        'indexes': [
            {'fields': ['idea', 'user'], 'unique': True}
        ]
    }

class JoinRequest(Document):
    idea = ReferenceField(Idea, required=True)
    user = ReferenceField(User, required=True)
    note = StringField()
    status = StringField(choices=["pending", "approved", "rejected"], default="pending")
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    admin_note = StringField()
    recommended_by_ai = BooleanField(default=False)
    ai_score = FloatField()
    skills_matched = ListField(StringField())
    meta = {
        'indexes': [
            {'fields': ['idea', 'user'], 'unique': True}
        ]
    }
