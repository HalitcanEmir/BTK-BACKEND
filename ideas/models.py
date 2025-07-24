from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField
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
    status = StringField(default='pending', choices=['pending', 'approved', 'rejected'])
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
