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
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Social Features
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)  # Store LinkedIn, Twitter, etc.
    is_verified = models.BooleanField(default=False)
    privacy_settings = models.JSONField(default=dict, blank=True)  # Profile visibility settings
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def is_mentor(self):
        return self.role == 'mentor'
    
    @property
    def is_learner(self):
        return self.role == 'learner'

# Advanced Social Features
class Follow(models.Model):
    """Follow relationship between users (learners following mentors)"""
    follower = models.ForeignKey('User', on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey('User', on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class PersonalMessage(models.Model):
    """Personal chat messages between users"""
    sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey('User', on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

class UserActivity(models.Model):
    """Track all user activities for profile activity feed"""
    ACTIVITY_TYPES = [
        ('session_created', 'Created a session'),
        ('session_completed', 'Completed a session'),
        ('feedback_given', 'Gave feedback'),
        ('feedback_received', 'Received feedback'),
        ('profile_updated', 'Updated profile'),
        ('new_follower', 'Got a new follower'),
        ('started_following', 'Started following someone'),
        ('session_booked', 'Booked a session'),
        ('achievement_earned', 'Earned an achievement'),
    ]
    
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    related_user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='related_activities')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.description}"

class UserSocialStats(models.Model):
    """Social statistics for each user"""
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='social_stats')
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    profile_views_count = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_rating = models.FloatField(default=0.0)
    response_time_hours = models.FloatField(default=24.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Social stats for {self.user.username}"
    
    def update_stats(self):
        """Update all social statistics"""
        self.followers_count = self.user.followers.count()
        self.following_count = self.user.following.count()
        # Update session and earnings stats if needed
        self.save()
    
    @property
    def is_mentor(self):
        return self.role == 'mentor'
    
    @property
    def is_learner(self):
        return self.role == 'learner'
