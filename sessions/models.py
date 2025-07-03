import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

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
    
    # Enhanced session tracking
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    actual_duration = models.IntegerField(null=True, blank=True, help_text="Actual session duration in minutes")
    
    # Session settings
    auto_start = models.BooleanField(default=False, help_text="Automatically start session at scheduled time")
    allow_late_join = models.BooleanField(default=True, help_text="Allow learners to join after session starts")
    require_approval = models.BooleanField(default=False, help_text="Require mentor approval for bookings")
    
    class Meta:
        ordering = ['-schedule']
    
    def __str__(self):
        return f"{self.title} by {self.mentor.username}"
    
    def clean(self):
        """Validate session data"""
        if self.schedule and self.schedule <= timezone.now():
            raise ValidationError("Session schedule must be in the future")
        
        if self.duration <= 0:
            raise ValidationError("Session duration must be positive")
        
        if self.max_participants <= 0:
            raise ValidationError("Maximum participants must be positive")
    
    @property
    def current_participants(self):
        if self.status == 'live':
            # For live sessions, count actual connected participants
            return self.active_participants.filter(left_at__isnull=True).count()
        else:
            # For non-live sessions, count confirmed bookings
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
    
    @property
    def is_live(self):
        return self.status == 'live' and self.started_at is not None
    
    @property
    def is_completed(self):
        return self.status == 'completed' and self.ended_at is not None
    
    @property
    def remaining_spots(self):
        return max(0, self.max_participants - self.current_participants)
    
    @property
    def session_progress(self):
        """Calculate session progress percentage"""
        if not self.is_live or not self.started_at:
            return 0
        
        elapsed = timezone.now() - self.started_at
        total_duration = timezone.timedelta(minutes=self.duration)
        progress = min(100, (elapsed.total_seconds() / total_duration.total_seconds()) * 100)
        return round(progress, 1)
    
    def start_session(self):
        """Start the session"""
        if not self.can_start:
            raise ValidationError("Session cannot be started yet")
        
        self.status = 'live'
        self.started_at = timezone.now()
        self.save()
        
        # Create notifications for all participants
        from .signals import create_session_start_notification
        create_session_start_notification(self)
    
    def end_session(self):
        """End the session"""
        if not self.is_live:
            raise ValidationError("Session is not live")
        
        self.status = 'completed'
        self.ended_at = timezone.now()
        
        # Calculate actual duration
        if self.started_at:
            duration = self.ended_at - self.started_at
            self.actual_duration = int(duration.total_seconds() / 60)
        
        self.save()
        
        # Create notifications for feedback
        from .signals import create_session_end_notification
        create_session_end_notification(self)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_ready = models.BooleanField(default=False)
    
    # Enhanced booking tracking
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    attendance_duration = models.IntegerField(null=True, blank=True, help_text="Attendance duration in minutes")
    
    # Payment tracking
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ])
    payment_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['learner', 'session']
    
    def __str__(self):
        return f"{self.learner.username} -> {self.session.title}"
    
    @property
    def is_active(self):
        return self.status in ['confirmed', 'attended']
    
    @property
    def can_join(self):
        return (self.is_active and 
                self.session.is_live and 
                (self.session.allow_late_join or not self.joined_at))
    
    def mark_joined(self):
        """Mark user as joined to session"""
        if not self.can_join:
            raise ValidationError("Cannot join session")
        
        self.joined_at = timezone.now()
        self.status = 'attended'
        self.save()
    
    def mark_left(self):
        """Mark user as left session"""
        if self.joined_at and not self.left_at:
            self.left_at = timezone.now()
            
            # Calculate attendance duration
            duration = self.left_at - self.joined_at
            self.attendance_duration = int(duration.total_seconds() / 60)
            
            self.save()

class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Enhanced feedback
    session_quality = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    mentor_effectiveness = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    content_relevance = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    technical_quality = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    class Meta:
        unique_together = ['session', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.session.title} ({self.rating}/5)"
    
    @property
    def average_rating(self):
        """Calculate average of all rating fields"""
        ratings = [self.rating]
        if self.session_quality:
            ratings.append(self.session_quality)
        if self.mentor_effectiveness:
            ratings.append(self.mentor_effectiveness)
        if self.content_relevance:
            ratings.append(self.content_relevance)
        if self.technical_quality:
            ratings.append(self.technical_quality)
        
        return sum(ratings) / len(ratings) if ratings else 0

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
        ('session_started', 'Session Started'),
        ('session_ended', 'Session Ended'),
        ('feedback_requested', 'Feedback Requested'),
        ('mentor_ready', 'Mentor Ready'),
        ('learner_ready', 'Learner Ready'),
        ('mentor_ready_status', 'Mentor Ready Status'),
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
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
        self.save()

class SessionParticipant(models.Model):
    """Track active participants in live sessions with advanced features"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='active_participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_mentor = models.BooleanField(default=False)
    
    # Connection and network status
    connection_status = models.CharField(max_length=20, default='connected', choices=[
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('reconnecting', 'Reconnecting'),
        ('connecting', 'Connecting'),
    ])
    
    network_quality = models.CharField(max_length=20, default='High', choices=[
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
        ('Poor', 'Poor'),
    ])
    
    # User status during session
    is_muted = models.BooleanField(default=False)
    is_video_off = models.BooleanField(default=False)
    is_screen_sharing = models.BooleanField(default=False)
    is_recording = models.BooleanField(default=False)
    
    # Session engagement metrics
    last_activity = models.DateTimeField(auto_now=True)
    total_connection_time = models.IntegerField(default=0, help_text="Total connection time in seconds")
    reconnection_count = models.IntegerField(default=0, help_text="Number of reconnections")
    
    # Technical metrics
    packet_loss = models.FloatField(default=0.0, help_text="Packet loss percentage")
    latency = models.FloatField(default=0.0, help_text="Latency in milliseconds")
    bandwidth = models.FloatField(default=0.0, help_text="Available bandwidth in Mbps")
    
    # User preferences and settings
    preferred_audio_device = models.CharField(max_length=100, blank=True)
    preferred_video_device = models.CharField(max_length=100, blank=True)
    audio_level = models.FloatField(default=1.0, help_text="Audio volume level (0.0 to 1.0)")
    
    class Meta:
        unique_together = ['session', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.session.title}"
    
    @property
    def is_active(self):
        return self.left_at is None and self.connection_status == 'connected'
    
    @property
    def connection_duration(self):
        """Calculate current connection duration in seconds"""
        if self.left_at:
            return int((self.left_at - self.joined_at).total_seconds())
        return int((timezone.now() - self.joined_at).total_seconds())
    
    @property
    def network_quality_color(self):
        """Get CSS color class for network quality"""
        quality_colors = {
            'High': 'text-green-500',
            'Medium': 'text-yellow-500',
            'Low': 'text-orange-500',
            'Poor': 'text-red-500',
        }
        return quality_colors.get(self.network_quality, 'text-gray-500')
    
    @property
    def status_summary(self):
        """Get a summary of user's current status"""
        status_parts = []
        
        if self.is_muted:
            status_parts.append("Muted")
        if self.is_video_off:
            status_parts.append("Video Off")
        if self.is_screen_sharing:
            status_parts.append("Screen Sharing")
        if self.is_recording:
            status_parts.append("Recording")
        
        return ", ".join(status_parts) if status_parts else "Active"
    
    def mark_left(self):
        """Mark participant as left"""
        self.left_at = timezone.now()
        self.connection_status = 'disconnected'
        self.total_connection_time = self.connection_duration
        self.save()
    
    def update_network_quality(self, quality):
        """Update network quality"""
        self.network_quality = quality
        self.save()
    
    def update_connection_status(self, status):
        """Update connection status"""
        if status == 'connected' and self.connection_status == 'reconnecting':
            self.reconnection_count += 1
        self.connection_status = status
        self.save()
    
    def update_technical_metrics(self, packet_loss=None, latency=None, bandwidth=None):
        """Update technical metrics"""
        if packet_loss is not None:
            self.packet_loss = packet_loss
        if latency is not None:
            self.latency = latency
        if bandwidth is not None:
            self.bandwidth = bandwidth
        self.save()
    
    def toggle_mute(self):
        """Toggle mute status"""
        self.is_muted = not self.is_muted
        self.save()
    
    def toggle_video(self):
        """Toggle video status"""
        self.is_video_off = not self.is_video_off
        self.save()
    
    def toggle_screen_sharing(self):
        """Toggle screen sharing status"""
        self.is_screen_sharing = not self.is_screen_sharing
        self.save()
    
    def toggle_recording(self):
        """Toggle recording status"""
        self.is_recording = not self.is_recording
        self.save()
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save()
