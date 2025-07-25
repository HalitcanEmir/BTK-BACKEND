from django.db import models
from mongoengine import Document, BooleanField, DateTimeField, StringField

# Create your models here.

class Project(Document):
    is_completed = BooleanField(default=False)
    completed_at = DateTimeField()
    success_label = StringField()
