from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Session, Booking, Notification, SessionParticipant
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

User = get_user_model()

def create_session_start_notification(session):
    """Create notifications when session starts"""
    # Notify all confirmed participants
    for booking in session.bookings.filter(status='confirmed'):
        Notification.objects.create(
            user=booking.learner,
            type='session_started',
            title=f'Session Started: {session.title}',
            message=f'Your session "{session.title}" has started. Click here to join!',
            related_session=session
        )
    
    # Send WebSocket notification
    channel_layer = get_channel_layer()
    for booking in session.bookings.filter(status='confirmed'):
        async_to_sync(channel_layer.group_send)(
            f'user_{booking.learner.id}',
            {
                'type': 'notification',
                'message': {
                    'type': 'session_started',
                    'title': f'Session Started: {session.title}',
                    'message': 'Your session has started. Click here to join!',
                    'session_id': str(session.id)
                }
            }
        )

def create_session_end_notification(session):
    """Create notifications when session ends"""
    # Notify all participants for feedback
    for booking in session.bookings.filter(status__in=['confirmed', 'attended']):
        Notification.objects.create(
            user=booking.learner,
            type='feedback_requested',
            title=f'Feedback Requested: {session.title}',
            message=f'Please provide feedback for your session "{session.title}".',
            related_session=session
        )
    
    # Notify mentor
    Notification.objects.create(
        user=session.mentor,
        type='session_ended',
        title=f'Session Ended: {session.title}',
        message=f'Your session "{session.title}" has ended. View feedback from participants.',
        related_session=session
    )

def create_booking_notification(booking):
    """Create notifications for new bookings"""
    # Notify mentor
    Notification.objects.create(
        user=booking.session.mentor,
        type='booking_confirmed',
        title=f'New Booking: {booking.session.title}',
        message=f'{booking.learner.username} has booked your session "{booking.session.title}".',
        related_session=booking.session
    )
    
    # Notify learner
    Notification.objects.create(
        user=booking.learner,
        type='booking_confirmed',
        title=f'Booking Confirmed: {booking.session.title}',
        message=f'Your booking for "{booking.session.title}" has been confirmed.',
        related_session=booking.session
    )

@receiver(post_save, sender=Session)
def session_status_changed(sender, instance, created, **kwargs):
    """Handle session status changes"""
    if created:
        return
    
    # Check if session was just started
    if instance.status == 'live' and instance.started_at:
        create_session_start_notification(instance)
    
    # Check if session was just ended
    if instance.status == 'completed' and instance.ended_at:
        create_session_end_notification(instance)

@receiver(post_save, sender=Booking)
def booking_created(sender, instance, created, **kwargs):
    """Handle new bookings"""
    if created and instance.status == 'confirmed':
        create_booking_notification(instance)

@receiver(post_save, sender=SessionParticipant)
def participant_joined(sender, instance, created, **kwargs):
    """Handle participant joining"""
    if created:
        # Notify other participants
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'session_{instance.session.id}',
            {
                'type': 'user_joined',
                'user_id': str(instance.user.id),
                'username': instance.user.username,
                'is_mentor': instance.is_mentor,
            }
        )

@receiver(post_save, sender=SessionParticipant)
def participant_left(sender, instance, **kwargs):
    """Handle participant leaving"""
    if instance.left_at:
        # Notify other participants
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'session_{instance.session.id}',
            {
                'type': 'user_left',
                'user_id': str(instance.user.id),
                'username': instance.user.username,
            }
        )

# Scheduled task functions for reminders
def send_session_reminders():
    """Send reminders for upcoming sessions"""
    from datetime import timedelta
    
    # Send reminders 10 minutes before session
    reminder_time = timezone.now() + timedelta(minutes=10)
    upcoming_sessions = Session.objects.filter(
        status='scheduled',
        schedule__lte=reminder_time,
        schedule__gt=timezone.now()
    )
    
    for session in upcoming_sessions:
        for booking in session.bookings.filter(status='confirmed'):
            Notification.objects.create(
                user=booking.learner,
                type='session_reminder',
                title=f'Session Reminder: {session.title}',
                message=f'Your session "{session.title}" starts in 10 minutes.',
                related_session=session
            )

def auto_start_sessions():
    """Automatically start sessions that are scheduled to start"""
    now = timezone.now()
    auto_start_sessions = Session.objects.filter(
        status='scheduled',
        auto_start=True,
        schedule__lte=now,
        schedule__gte=now - timedelta(minutes=5)  # Within last 5 minutes
    )
    
    for session in auto_start_sessions:
        try:
            session.start_session()
        except Exception as e:
            print(f"Failed to auto-start session {session.id}: {e}")

def cleanup_expired_tokens():
    """Clean up expired room tokens"""
    from .models import RoomToken
    
    expired_tokens = RoomToken.objects.filter(expires_at__lt=timezone.now())
    expired_tokens.delete() 