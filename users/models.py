import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('mentor', 'Mentor'),
        ('learner', 'Learner'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='learner')
    bio = models.TextField(blank=True, null=True)
    expertise = models.JSONField(default=list, blank=True)  # List of skills/domains
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def is_mentor(self):
        return self.role == 'mentor'
    
    @property
    def is_learner(self):
        return self.role == 'learner'
