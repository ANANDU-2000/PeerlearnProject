"""
Session Management System - Track Past, Active and Future Sessions
Real Database Implementation for Session History and Time Management
"""

from django.utils import timezone
from django.db.models import Q
from .models import Session, Booking, Feedback
from datetime import datetime, timedelta

class SessionManager:
    """Manage session lifecycle and history tracking"""
    
    @staticmethod
    def get_session_status(session):
        """Determine current session status based on timing"""
        now = timezone.now()
        session_start = session.schedule
        session_end = session_start + timedelta(minutes=session.duration)
        
        if now < session_start - timedelta(minutes=15):
            return 'upcoming'
        elif now < session_start:
            return 'starting_soon'
        elif now <= session_end:
            return 'live'
        else:
            return 'completed'
    
    @staticmethod
    def get_learner_sessions(user):
        """Get categorized sessions for learner"""
        bookings = Booking.objects.filter(
            learner=user,
            status='confirmed'
        ).select_related('session', 'session__mentor').order_by('-session__schedule')
        
        sessions = {
            'upcoming': [],
            'live': [],
            'completed': []
        }
        
        for booking in bookings:
            status = SessionManager.get_session_status(booking.session)
            
            session_data = {
                'booking': booking,
                'session': booking.session,
                'status': status,
                'can_join': status in ['starting_soon', 'live'],
                'can_rate': status == 'completed' and not hasattr(booking.session, 'feedback_set'),
                'time_until_start': None,
                'has_feedback': Feedback.objects.filter(
                    session=booking.session, 
                    user=user
                ).exists()
            }
            
            if status == 'upcoming':
                time_until = booking.session.schedule - timezone.now()
                session_data['time_until_start'] = time_until
                sessions['upcoming'].append(session_data)
            elif status in ['starting_soon', 'live']:
                sessions['live'].append(session_data)
            else:
                sessions['completed'].append(session_data)
        
        return sessions
    
    @staticmethod
    def mark_session_completed(session_id):
        """Mark session as completed and trigger feedback collection"""
        try:
            session = Session.objects.get(id=session_id)
            session.status = 'completed'
            session.save()
            
            # Update all confirmed bookings
            Booking.objects.filter(
                session=session,
                status='confirmed'
            ).update(status='completed')
            
            return True
        except Session.DoesNotExist:
            return False
    
    @staticmethod
    def get_session_history_stats(user):
        """Get user's session history statistics"""
        completed_bookings = Booking.objects.filter(
            learner=user,
            status__in=['completed', 'confirmed']
        ).select_related('session')
        
        total_sessions = completed_bookings.count()
        total_hours = sum([
            booking.session.duration / 60 
            for booking in completed_bookings 
            if SessionManager.get_session_status(booking.session) == 'completed'
        ])
        
        # Get rating average
        user_feedback = Feedback.objects.filter(user=user)
        avg_rating = user_feedback.aggregate(
            avg=models.Avg('rating')
        )['avg'] or 0
        
        return {
            'total_sessions': total_sessions,
            'total_hours': round(total_hours, 1),
            'average_rating_given': round(avg_rating, 1),
            'mentors_learned_from': completed_bookings.values('session__mentor').distinct().count()
        }
    
    @staticmethod
    def auto_complete_overdue_sessions():
        """Auto-complete sessions that have passed their end time"""
        now = timezone.now()
        
        # Find sessions that should be completed
        overdue_sessions = Session.objects.filter(
            status__in=['scheduled', 'live']
        )
        
        completed_count = 0
        for session in overdue_sessions:
            session_end = session.schedule + timedelta(minutes=session.duration)
            if now > session_end:
                SessionManager.mark_session_completed(session.id)
                completed_count += 1
        
        return completed_count

def get_session_time_display(session):
    """Get human-readable time display for session"""
    now = timezone.now()
    session_start = session.schedule
    
    if now < session_start:
        # Future session
        time_diff = session_start - now
        if time_diff.days > 0:
            return f"In {time_diff.days} days"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"In {hours} hours"
        else:
            minutes = time_diff.seconds // 60
            return f"In {minutes} minutes"
    else:
        # Past session
        time_diff = now - session_start
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"{hours} hours ago"
        else:
            minutes = time_diff.seconds // 60
            return f"{minutes} minutes ago"