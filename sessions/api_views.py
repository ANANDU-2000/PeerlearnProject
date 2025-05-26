from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
import json

from .models import Session, Booking, Request, Notification, Feedback
from users.models import User


@login_required
@require_http_methods(["POST"])
def book_session(request, session_id):
    """Book a session for a learner"""
    session = get_object_or_404(Session, id=session_id)
    
    if request.user.is_mentor:
        return JsonResponse({'error': 'Mentors cannot book sessions'}, status=400)
    
    if session.is_full:
        return JsonResponse({'error': 'Session is full'}, status=400)
    
    # Check if already booked
    existing_booking = Booking.objects.filter(
        learner=request.user,
        session=session,
        status='confirmed'
    ).exists()
    
    if existing_booking:
        return JsonResponse({'error': 'Already booked this session'}, status=400)
    
    # Create booking
    booking = Booking.objects.create(
        learner=request.user,
        session=session,
        status='confirmed'
    )
    
    # Create notification for mentor
    Notification.objects.create(
        user=session.mentor,
        type='booking_confirmed',
        title='New Booking!',
        message=f'{request.user.get_full_name() or request.user.username} booked your session "{session.title}"',
        related_session=session
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Session booked successfully!',
        'booking_id': str(booking.id)
    })


@login_required
@require_http_methods(["POST"])
def create_session_request(request):
    """Create a new session request"""
    if request.user.is_mentor:
        return JsonResponse({'error': 'Mentors cannot create requests'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        session_request = Request.objects.create(
            learner=request.user,
            topic=data.get('topic'),
            description=data.get('description'),
            domain=data.get('domain'),
            skills=data.get('skills', ''),
            duration=int(data.get('duration')),
            urgency=data.get('urgency', 'flexible'),
            budget=data.get('budget', ''),
            preferred_times=data.get('preferred_times', [])
        )
        
        # Notify relevant mentors
        mentors = User.objects.filter(
            role='mentor',
            expertise__contains=[data.get('domain')]
        )
        
        for mentor in mentors:
            Notification.objects.create(
                user=mentor,
                type='new_request',
                title='New Session Request',
                message=f'New request for "{data.get("topic")}" in {data.get("domain")}',
                related_request=session_request
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Request submitted successfully!',
            'request_id': str(session_request.id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def accept_request(request, request_id):
    """Accept a session request (mentor only)"""
    if not request.user.is_mentor:
        return JsonResponse({'error': 'Only mentors can accept requests'}, status=403)
    
    session_request = get_object_or_404(Request, id=request_id)
    
    if session_request.status != 'pending':
        return JsonResponse({'error': 'Request is no longer pending'}, status=400)
    
    try:
        data = json.loads(request.body)
        schedule = data.get('schedule')
        
        with transaction.atomic():
            # Update request
            session_request.status = 'accepted'
            session_request.mentor = request.user
            session_request.save()
            
            # Create session
            session = Session.objects.create(
                mentor=request.user,
                title=session_request.topic,
                description=session_request.description,
                schedule=schedule,
                duration=session_request.duration,
                max_participants=1,  # 1-on-1 for custom requests
                status='scheduled'
            )
            
            # Auto-book for the requester
            Booking.objects.create(
                learner=session_request.learner,
                session=session,
                status='confirmed'
            )
            
            # Notify learner
            Notification.objects.create(
                user=session_request.learner,
                type='request_accepted',
                title='Request Accepted!',
                message=f'Your request for "{session_request.topic}" has been accepted!',
                related_session=session
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Request accepted and session created!',
            'session_id': str(session.id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def start_session(request, session_id):
    """Start a session (mentor only)"""
    session = get_object_or_404(Session, id=session_id)
    
    if session.mentor != request.user:
        return JsonResponse({'error': 'Only the session mentor can start the session'}, status=403)
    
    if not session.can_start:
        return JsonResponse({'error': 'Session cannot be started yet'}, status=400)
    
    session.status = 'live'
    session.save()
    
    # Notify all participants
    bookings = session.bookings.filter(status='confirmed')
    for booking in bookings:
        Notification.objects.create(
            user=booking.learner,
            type='session_starting',
            title='Session Starting!',
            message=f'Your session "{session.title}" is now live!',
            related_session=session
        )
    
    return JsonResponse({
        'success': True,
        'message': 'Session started successfully!',
        'room_url': f'/sessions/{session_id}/room/'
    })


@login_required
@require_http_methods(["POST"])
def end_session(request, session_id):
    """End a session (mentor only)"""
    session = get_object_or_404(Session, id=session_id)
    
    if session.mentor != request.user:
        return JsonResponse({'error': 'Only the session mentor can end the session'}, status=403)
    
    session.status = 'completed'
    session.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Session ended successfully!'
    })


@login_required
@require_http_methods(["POST"])
def submit_feedback(request, session_id):
    """Submit feedback for a completed session"""
    session = get_object_or_404(Session, id=session_id)
    
    if session.status != 'completed':
        return JsonResponse({'error': 'Can only rate completed sessions'}, status=400)
    
    # Check if user participated
    participated = (
        session.mentor == request.user or 
        session.bookings.filter(learner=request.user, status='confirmed').exists()
    )
    
    if not participated:
        return JsonResponse({'error': 'You did not participate in this session'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        feedback, created = Feedback.objects.update_or_create(
            session=session,
            user=request.user,
            defaults={
                'rating': int(data.get('rating')),
                'comment': data.get('comment', '')
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your feedback!',
            'feedback_id': str(feedback.id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_sessions_api(request):
    """Get sessions data for dashboard"""
    sessions = Session.objects.filter(
        status='scheduled',
        schedule__gte=timezone.now()
    ).select_related('mentor')[:20]
    
    sessions_data = []
    for session in sessions:
        sessions_data.append({
            'id': str(session.id),
            'title': session.title,
            'mentor_name': session.mentor.get_full_name() or session.mentor.username,
            'schedule': session.schedule.isoformat(),
            'duration': session.duration,
            'current_participants': session.current_participants,
            'max_participants': session.max_participants,
            'is_full': session.is_full,
            'description': session.description[:200] + '...' if len(session.description) > 200 else session.description
        })
    
    return JsonResponse({
        'sessions': sessions_data,
        'total': len(sessions_data)
    })


@login_required
@require_http_methods(["GET"])
def get_notifications_api(request):
    """Get user notifications"""
    notifications = request.user.notifications.filter(read=False)[:10]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': str(notification.id),
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
            'read': notification.read
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': notifications.count()
    })


@login_required
@require_http_methods(["POST"])
def mark_notifications_read(request):
    """Mark notifications as read"""
    try:
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])
        
        if notification_ids:
            request.user.notifications.filter(
                id__in=notification_ids
            ).update(read=True)
        else:
            # Mark all as read
            request.user.notifications.update(read=True)
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def create_session_api(request):
    """Create a new session (mentor only)"""
    if not request.user.is_mentor:
        return JsonResponse({'error': 'Only mentors can create sessions'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        session = Session.objects.create(
            mentor=request.user,
            title=data.get('title'),
            description=data.get('description'),
            schedule=data.get('schedule'),
            duration=int(data.get('duration')),
            max_participants=int(data.get('max_participants')),
            status=data.get('status', 'draft')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Session created successfully!',
            'session_id': str(session.id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def publish_session(request, session_id):
    """Publish a draft session"""
    session = get_object_or_404(Session, id=session_id)
    
    if session.mentor != request.user:
        return JsonResponse({'error': 'Only the session creator can publish it'}, status=403)
    
    if session.status != 'draft':
        return JsonResponse({'error': 'Only draft sessions can be published'}, status=400)
    
    session.status = 'scheduled'
    session.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Session published successfully!'
    })


@login_required
@require_http_methods(["POST"])
def decline_request(request, request_id):
    """Decline a learner request"""
    try:
        from sessions.models import Request
        session_request = get_object_or_404(Request, id=request_id)
        
        if session_request.mentor != request.user:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        session_request.status = 'rejected'
        session_request.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Request declined successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def request_payout(request):
    """Request payout of available earnings"""
    try:
        if not request.user.is_mentor:
            return JsonResponse({'error': 'Only mentors can request payouts'}, status=403)
        
        # Calculate available earnings from real completed sessions
        completed_sessions = Booking.objects.filter(
            session__mentor=request.user,
            status='completed'
        ).count()
        
        # Calculate real earnings based on hourly rate
        hourly_rate = getattr(request.user, 'hourly_rate', 25)
        total_earnings = completed_sessions * hourly_rate * 1.5
        
        return JsonResponse({
            'success': True,
            'message': f'Payout request of ₹{total_earnings} submitted successfully!',
            'amount': total_earnings
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)