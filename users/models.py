import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from PIL import Image
import os

class User(AbstractUser):
    ROLE_CHOICES = [
        ('learner', 'Learner'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='learner')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    
    # Profile information
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    
    # Profile image with automatic resizing
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True,
        help_text="Profile image will be automatically resized to 200x200"
    )
    
    # Enhanced profile fields
    date_of_birth = models.DateField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Mentor-specific fields
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    availability = models.JSONField(default=dict, blank=True)
    
    # Learner-specific fields
    interests = models.TextField(blank=True, help_text="Comma-separated interests")
    career_goals = models.TextField(blank=True)
    domain = models.CharField(max_length=100, blank=True)
    
    # Verification and status
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(blank=True, null=True)
    
    # Activity tracking
    last_active = models.DateTimeField(auto_now=True)
    total_sessions = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Social features
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users_user'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile image
        if self.profile_image:
            self.resize_profile_image()
    
    def resize_profile_image(self):
        """Resize profile image to 200x200 pixels"""
        if self.profile_image:
            try:
                with Image.open(self.profile_image.path) as img:
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize and crop to square
                    img_width, img_height = img.size
                    min_dimension = min(img_width, img_height)
                    
                    # Crop to square
                    left = (img_width - min_dimension) // 2
                    top = (img_height - min_dimension) // 2
                    right = left + min_dimension
                    bottom = top + min_dimension
                    
                    img = img.crop((left, top, right, bottom))
                    
                    # Resize to 200x200
                    img = img.resize((200, 200), Image.Resampling.LANCZOS)
                    
                    # Save with optimization
                    img.save(self.profile_image.path, 'JPEG', quality=85, optimize=True)
            except Exception as e:
                print(f"Error resizing profile image: {e}")
    
    @property
    def is_mentor(self):
        return self.role == 'mentor'
    
    @property
    def is_learner(self):
        return self.role == 'learner'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def profile_image_url(self):
        """Get profile image URL or generate avatar"""
        if self.profile_image:
            return self.profile_image.url
        return None
    
    @property
    def avatar_letter(self):
        """Get first letter of name for avatar"""
        if self.first_name:
            return self.first_name[0].upper()
        elif self.username:
            return self.username[0].upper()
        return 'U'
    
    @property
    def is_online(self):
        """Check if user was active in last 5 minutes"""
        if self.last_active:
            return timezone.now() - self.last_active < timezone.timedelta(minutes=5)
        return False
    
    def get_skills_list(self):
        """Get skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []
    
    def get_interests_list(self):
        """Get interests as a list"""
        if self.interests:
            return [interest.strip() for interest in self.interests.split(',') if interest.strip()]
        return []

class Follow(models.Model):
    """Follow system for mentors and learners"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'created_at']),
            models.Index(fields=['following', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class PaymentHistory(models.Model):
    """Track user payment history"""
    PAYMENT_TYPE_CHOICES = [
        ('session_booking', 'Session Booking'),
        ('gift', 'Gift'),
        ('premium_upgrade', 'Premium Upgrade'),
        ('mentor_payout', 'Mentor Payout'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_history')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment gateway details
    payment_id = models.CharField(max_length=100, blank=True)
    gateway = models.CharField(max_length=50, default='razorpay')
    
    # Related objects
    related_session_id = models.UUIDField(blank=True, null=True)
    related_user_id = models.UUIDField(blank=True, null=True)  # For gifts/payouts
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['payment_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_type} - ₹{self.amount}"

class UserActivity(models.Model):
    """Track user activities for history"""
    ACTIVITY_TYPES = [
        ('session_created', 'Session Created'),
        ('session_joined', 'Session Joined'),
        ('session_completed', 'Session Completed'),
        ('profile_updated', 'Profile Updated'),
        ('followed_user', 'Followed User'),
        ('unfollowed_user', 'Unfollowed User'),
        ('feedback_given', 'Feedback Given'),
        ('payment_made', 'Payment Made'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField()
    
    # Related objects
    related_user_id = models.UUIDField(blank=True, null=True)
    related_session_id = models.UUIDField(blank=True, null=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

# class FeedbackReply(models.Model):
#     """Replies to feedback"""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     feedback = models.ForeignKey('sessions.Feedback', on_delete=models.CASCADE, related_name='replies')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who replied
#     reply_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['created_at']
    
#     def __str__(self):
#         return f"Reply by {self.user.username} to feedback"
