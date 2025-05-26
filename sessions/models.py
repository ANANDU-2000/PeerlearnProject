import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Session(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Category choices for ML recommendations
    CATEGORY_CHOICES = [
        ('programming', 'Programming & Development'),
        ('data-science', 'Data Science & Analytics'),
        ('web-development', 'Web Development'),
        ('mobile-development', 'Mobile Development'),
        ('ai-ml', 'AI & Machine Learning'),
        ('design', 'UI/UX Design'),
        ('business', 'Business & Marketing'),
        ('language', 'Language Learning'),
        ('music', 'Music & Arts'),
        ('fitness', 'Health & Fitness'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_sessions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='session_thumbnails/', blank=True, null=True, help_text="Session cover image")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, help_text="Session category for recommendations")
    skills = models.TextField(blank=True, help_text="Comma-separated skills for ML matching")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Price in INR, null for free sessions")
    schedule = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    max_participants = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-schedule']
    
    def __str__(self):
        return f"{self.title} by {self.mentor.username}"
    
    @property
    def current_participants(self):
        return self.bookings.filter(status='confirmed').count()
    
    @property
    def is_full(self):
        return self.current_participants >= self.max_participants
    
    @property
    def can_start(self):
        now = timezone.now()
        return (now >= self.schedule - timezone.timedelta(minutes=15) and 
                self.status == 'scheduled')
    
    @property
    def is_upcoming(self):
        return self.schedule > timezone.now() and self.status in ['scheduled', 'draft']

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['learner', 'session']
    
    def __str__(self):
        return f"{self.learner.username} -> {self.session.title}"

class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.session.title} ({self.rating}/5)"

class Request(models.Model):
    """Custom session requests from learners"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    URGENCY_CHOICES = [
        ('today', 'Today'),
        ('tomorrow', 'Tomorrow'),
        ('this-week', 'This Week'),
        ('next-week', 'Next Week'),
        ('flexible', 'Flexible'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_requests')
    topic = models.CharField(max_length=200)
    description = models.TextField()
    domain = models.CharField(max_length=50)
    skills = models.CharField(max_length=500, blank=True)
    duration = models.IntegerField(help_text="Preferred duration in minutes")
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='flexible')
    budget = models.CharField(max_length=50, blank=True)
    preferred_times = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Request: {self.topic} by {self.learner.username}"

class RoomToken(models.Model):
    """Temporary tokens for WebRTC room access"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        return timezone.now() < self.expires_at

class Notification(models.Model):
    """Real-time notifications for users"""
    TYPE_CHOICES = [
        ('session_reminder', 'Session Reminder'),
        ('session_starting', 'Session Starting'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('session_cancelled', 'Session Cancelled'),
        ('new_request', 'New Request'),
        ('request_accepted', 'Request Accepted'),
        ('request_rejected', 'Request Rejected'),
        ('new_message', 'New Message'),
        ('payment_received', 'Payment Received'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)
    related_request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} for {self.user.username}"
