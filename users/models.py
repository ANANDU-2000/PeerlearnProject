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
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skills for recommendation matching")
    interests = models.CharField(max_length=500, blank=True, help_text="Learning interests for AI recommendations")
    domain = models.CharField(max_length=100, blank=True, help_text="Learning domain/field")
    expertise = models.CharField(max_length=100, blank=True, help_text="Primary domain/area of expertise")
    career_goals = models.TextField(blank=True, help_text="Career aspirations for AI guidance")
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Password Reset Fields
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
    
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
