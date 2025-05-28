"""
Advanced User App Feedback System for PeerLearn
Handles user ratings, comments, and admin replies with email notifications
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class AppFeedback(models.Model):
    """Model for storing user feedback about the PeerLearn app"""
    
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]
    
    CATEGORY_CHOICES = [
        ('ui_ux', 'User Interface & Experience'),
        ('performance', 'Performance & Speed'),
        ('features', 'Features & Functionality'),
        ('support', 'Customer Support'),
        ('payment', 'Payment System'),
        ('video_quality', 'Video Quality'),
        ('mobile', 'Mobile Experience'),
        ('general', 'General Feedback'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Under Review'),
        ('replied', 'Admin Replied'),
        ('resolved', 'Resolved'),
        ('archived', 'Archived'),
    ]
    
    # User Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_feedback')
    email = models.EmailField(help_text="User's email for notifications")
    
    # Feedback Content
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating of the app (1-5 stars)"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of feedback"
    )
    title = models.CharField(max_length=200, help_text="Brief title for the feedback")
    message = models.TextField(help_text="Detailed feedback message")
    
    # Admin Management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the feedback"
    )
    admin_reply = models.TextField(blank=True, null=True, help_text="Admin's reply to the feedback")
    admin_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='admin_feedback_replies',
        help_text="Admin who replied to this feedback"
    )
    reply_sent_via_email = models.BooleanField(default=False, help_text="Whether reply was sent via email")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Fields
    user_agent = models.TextField(blank=True, help_text="User's browser/device info")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Featured feedback for testimonials")
    is_public = models.BooleanField(default=True, help_text="Show in public feedback")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'App Feedback'
        verbose_name_plural = 'App Feedback'
        indexes = [
            models.Index(fields=['rating', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['category', 'rating']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.rating}★ - {self.title[:50]}"
    
    def save(self, *args, **kwargs):
        # Set replied_at when admin reply is added
        if self.admin_reply and not self.replied_at:
            self.replied_at = timezone.now()
            if self.status == 'pending':
                self.status = 'replied'
        
        super().save(*args, **kwargs)
    
    @property
    def rating_stars(self):
        """Return star representation of rating"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    @property
    def time_since_created(self):
        """Return human-readable time since creation"""
        from django.utils.timesince import timesince
        return timesince(self.created_at)
    
    @property
    def is_new(self):
        """Check if feedback is new (less than 24 hours old)"""
        return (timezone.now() - self.created_at).days < 1
    
    @classmethod
    def get_average_rating(cls):
        """Get overall average rating for the app"""
        from django.db.models import Avg
        result = cls.objects.aggregate(avg_rating=Avg('rating'))
        return round(result['avg_rating'] or 0, 1)
    
    @classmethod
    def get_rating_distribution(cls):
        """Get distribution of ratings"""
        from django.db.models import Count
        return cls.objects.values('rating').annotate(count=Count('rating')).order_by('rating')
    
    @classmethod
    def get_pending_count(cls):
        """Get count of pending feedback requiring admin attention"""
        return cls.objects.filter(status='pending').count()
    
    @classmethod
    def get_weekly_feedback(cls):
        """Get feedback from the last 7 days"""
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        return cls.objects.filter(created_at__gte=week_ago)

class FeedbackNotification(models.Model):
    """Model for tracking feedback-related notifications"""
    
    NOTIFICATION_TYPES = [
        ('new_feedback', 'New Feedback Received'),
        ('admin_reply', 'Admin Reply Sent'),
        ('status_update', 'Status Updated'),
    ]
    
    feedback = models.ForeignKey(AppFeedback, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.feedback.title[:30]}"