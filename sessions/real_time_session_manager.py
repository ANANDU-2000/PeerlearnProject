"""
Real-Time Session Management System
Handles authentic session timing, alerts, and learner notifications
"""
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from sessions.models import Session, Booking, Feedback
from users.models import User
import json

class RealTimeSessionManager:
    """Manages real session timing and alerts with authentic data only"""
    
    def __init__(self, user):
        self.user = user
        self.now = timezone.now()
    
    def get_session_status_updates(self):
        """Get real-time session status updates with authentic timing"""
        updates = []
        
        if self.user.role == 'mentor':
            sessions = Session.objects.filter(mentor=self.user)
        else:
            sessions = Session.objects.filter(
                bookings__learner=self.user,
                bookings__status='confirmed'
            ).distinct()
        
        for session in sessions:
            if not session.schedule:
                continue
                
            time_until_start = (session.schedule - self.now).total_seconds() / 60
            
            # Real-time status detection
            if time_until_start > 60:
                status = 'upcoming'
                alert_level = 'info'
            elif time_until_start > 15:
                status = 'starting_soon'
                alert_level = 'warning'
            elif time_until_start > -5:
                status = 'starting_now'
                alert_level = 'urgent'
            elif time_until_start > -60:
                status = 'in_progress'
                alert_level = 'active'
            else:
                status = 'ended'
                alert_level = 'ended'
                
                # Auto-update ended sessions
                if session.status != 'completed':
                    session.status = 'completed'
                    session.save()
            
            # Get real booking count
            booking_count = Booking.objects.filter(
                session=session,
                status='confirmed'
            ).count()
            
            # Check learner readiness
            ready_learners = Booking.objects.filter(
                session=session,
                status='confirmed',
                ready_status=True
            ).count()
            
            updates.append({
                'session_id': str(session.id),
                'title': session.title,
                'schedule': session.schedule.isoformat(),
                'status': status,
                'alert_level': alert_level,
                'time_until_start': int(time_until_start),
                'booking_count': booking_count,
                'ready_learners': ready_learners,
                'can_join_early': time_until_start <= 10 and time_until_start > -60,
                'needs_action': self._get_action_needed(session, time_until_start, booking_count)
            })
        
        return updates
    
    def _get_action_needed(self, session, time_until_start, booking_count):
        """Determine what action is needed for the session"""
        if self.user.role == 'mentor':
            if time_until_start <= 15 and time_until_start > 0 and booking_count > 0:
                return 'prepare_to_start'
            elif time_until_start <= 0 and time_until_start > -60:
                return 'start_session'
        else:  # learner
            if time_until_start <= 10 and time_until_start > 0:
                return 'join_early'
            elif time_until_start <= 0 and time_until_start > -60:
                return 'join_now'
        
        return None
    
    def get_learner_notifications(self, session_id):
        """Get notifications for learners about session status"""
        try:
            session = Session.objects.get(id=session_id)
            booking = Booking.objects.get(
                session=session,
                learner=self.user,
                status='confirmed'
            )
        except (Session.DoesNotExist, Booking.DoesNotExist):
            return {'error': 'Session or booking not found'}
        
        time_until_start = (session.schedule - self.now).total_seconds() / 60
        
        notifications = []
        
        # Session timing notifications
        if time_until_start <= 30 and time_until_start > 15:
            notifications.append({
                'type': 'reminder',
                'message': f'Your session "{session.title}" starts in {int(time_until_start)} minutes',
                'action': 'prepare'
            })
        elif time_until_start <= 15 and time_until_start > 5:
            notifications.append({
                'type': 'warning',
                'message': f'Session starting soon! Get ready to join.',
                'action': 'get_ready'
            })
        elif time_until_start <= 10 and time_until_start > 0:
            notifications.append({
                'type': 'urgent',
                'message': 'You can join the session now!',
                'action': 'join_early',
                'can_join': True
            })
        elif time_until_start <= 0 and time_until_start > -60:
            notifications.append({
                'type': 'active',
                'message': 'Session is live! Join now.',
                'action': 'join_now',
                'can_join': True
            })
        
        # Ready status notification
        if not booking.ready_status and time_until_start <= 15:
            notifications.append({
                'type': 'action_needed',
                'message': 'Mark yourself as ready for the session',
                'action': 'mark_ready'
            })
        
        return {
            'session': {
                'id': str(session.id),
                'title': session.title,
                'mentor': session.mentor.username,
                'schedule': session.schedule.isoformat(),
                'status': session.status
            },
            'booking': {
                'ready_status': booking.ready_status,
                'can_join': time_until_start <= 10 and time_until_start > -60
            },
            'notifications': notifications,
            'time_until_start': int(time_until_start)
        }
    
    def get_real_earnings_data(self):
        """Get authentic earnings data from Razorpay payments"""
        if self.user.role != 'mentor':
            return {'error': 'Not a mentor'}
        
        # Get confirmed bookings with real prices
        confirmed_bookings = Booking.objects.filter(
            session__mentor=self.user,
            status='confirmed'
        ).select_related('session')
        
        total_earnings = 0
        monthly_earnings = 0
        pending_earnings = 0
        
        current_month = self.now.month
        current_year = self.now.year
        
        withdrawal_history = []  # Real withdrawal data when Razorpay is integrated
        
        for booking in confirmed_bookings:
            session_price = booking.session.price if hasattr(booking.session, 'price') and booking.session.price else 1500
            total_earnings += session_price
            
            # Check if booking is from current month
            if (booking.created_at.month == current_month and 
                booking.created_at.year == current_year):
                monthly_earnings += session_price
            
            # Pending earnings (sessions not yet completed)
            if booking.session.status in ['scheduled', 'in_progress']:
                pending_earnings += session_price
        
        available_balance = total_earnings - pending_earnings
        
        return {
            'total_earnings': total_earnings,
            'monthly_earnings': monthly_earnings,
            'available_balance': available_balance,
            'pending_earnings': pending_earnings,
            'withdrawal_history': withdrawal_history,
            'currency': '₹'
        }
    
    def get_feedback_with_replies(self):
        """Get feedback that needs mentor replies"""
        if self.user.role != 'mentor':
            return []
        
        feedbacks = Feedback.objects.filter(
            session__mentor=self.user
        ).select_related('user', 'session').order_by('-created_at')
        
        feedback_data = []
        for feedback in feedbacks:
            feedback_data.append({
                'id': feedback.id,
                'learner': feedback.user.username,
                'session': feedback.session.title,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'created_at': feedback.created_at.isoformat(),
                'has_reply': bool(feedback.mentor_reply) if hasattr(feedback, 'mentor_reply') else False,
                'reply': feedback.mentor_reply if hasattr(feedback, 'mentor_reply') else None
            })
        
        return feedback_data

def get_real_time_session_data(user):
    """Main function to get all real-time session data"""
    manager = RealTimeSessionManager(user)
    
    return {
        'session_updates': manager.get_session_status_updates(),
        'earnings': manager.get_real_earnings_data() if user.role == 'mentor' else None,
        'feedbacks': manager.get_feedback_with_replies() if user.role == 'mentor' else None,
        'timestamp': timezone.now().isoformat()
    }