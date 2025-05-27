"""
Advanced Follow System and Social Features for PeerLearn
Instagram/Facebook-like social interactions between mentors and learners
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

User = get_user_model()

class Follow(models.Model):
    """Follow relationship between users (learners following mentors)"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class PersonalMessage(models.Model):
    """Personal chat messages between users"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

class ProfileView(models.Model):
    """Track profile views for analytics"""
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_views')
    viewed_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_viewed_by')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('viewer', 'viewed_profile')
    
    def __str__(self):
        return f"{self.viewer.username} viewed {self.viewed_profile.username}'s profile"

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='related_activities')
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data like session_id, rating, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.description}"

class UserBadge(models.Model):
    """Achievement badges for users"""
    BADGE_TYPES = [
        ('mentor_expert', 'Expert Mentor'),
        ('top_rated', 'Top Rated'),
        ('quick_responder', 'Quick Responder'),
        ('popular_teacher', 'Popular Teacher'),
        ('dedicated_learner', 'Dedicated Learner'),
        ('feedback_champion', 'Feedback Champion'),
        ('session_master', '100 Sessions'),
        ('community_favorite', 'Community Favorite'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge_type')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_badge_type_display()}"

class UserSocialStats(models.Model):
    """Social statistics for each user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='social_stats')
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    profile_views_count = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_rating = models.FloatField(default=0.0)
    response_time_hours = models.FloatField(default=24.0)  # Average response time in hours
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Social stats for {self.user.username}"
    
    def update_stats(self):
        """Update all social statistics"""
        self.followers_count = self.user.followers.count()
        self.following_count = self.user.following.count()
        self.profile_views_count = self.user.profile_viewed_by.count()
        
        # Update session and earnings stats
        from sessions.models import Session, Booking, Feedback
        user_sessions = Session.objects.filter(mentor=self.user)
        self.total_sessions = user_sessions.count()
        
        # Calculate average rating from feedback
        user_feedback = Feedback.objects.filter(session__mentor=self.user)
        if user_feedback.exists():
            self.average_rating = user_feedback.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating'] or 0.0
        
        self.save()