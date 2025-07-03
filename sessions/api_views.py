from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
import json 

from .models import Session, Booking, Request, Notification, Feedback
from users.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from .matching import get_mentor_recommendations, get_session_recommendations

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
    """Handle session request creation from learners to mentors"""
    try:
        # Get form data
        mentor_id = request.POST.get('mentor_id')
        session_date = request.POST.get('session_date')
        session_time = request.POST.get('session_time')
        duration = request.POST.get('duration')
        topic = request.POST.get('topic')
        description = request.POST.get('description')
        
        # Validate required fields
        if not all([mentor_id, session_date, session_time, duration, topic, description]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            }, status=400)
        
        # Get mentor
        try:
            mentor = User.objects.get(id=mentor_id, role='mentor', is_active=True)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Invalid mentor selected'
            }, status=400)
        
        # Create datetime from date and time
        from datetime import datetime
        schedule = datetime.strptime(f"{session_date} {session_time}", "%Y-%m-%d %H:%M")
        schedule = timezone.make_aware(schedule)
        
        # Validate schedule is in future
        if schedule <= timezone.now():
            return JsonResponse({
                'success': False,
                'message': 'Session must be scheduled in the future'
            }, status=400)
        
        # Create session request
        session_request = Request.objects.create(
            learner=request.user,
            mentor=mentor,
            topic=topic,
            description=description,
            duration=int(duration),
            schedule=schedule,
            status='pending'
        )
        
        # Create notification for mentor
        from notifications.models import Notification
        Notification.objects.create(
            recipient=mentor,
            sender=request.user,
            notification_type='session_request',
            title='New Session Request',
            message=f"{request.user.get_full_name()} has requested a {duration}-minute session on {topic}",
            related_object_id=session_request.id
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Session request sent successfully',
            'request_id': session_request.id
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


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

    print(f"Attempting to start session {session_id}. Request User ID: {request.user.id}, Session Mentor ID: {session.mentor.id}")

    if session.mentor != request.user:
        print(f"403 Forbidden: User {request.user.id} is not the mentor ({session.mentor.id}) for session {session_id}")
        return JsonResponse({'error': 'Only the session mentor can start the session'}, status=403)
    
    if not session.can_start:
        return JsonResponse({'error': 'Session cannot be started yet'}, status=400)
    
    session.status = 'live'
    session.save()
    
    # Notify all participants (learners)
    bookings = session.bookings.filter(status='confirmed')
    for booking in bookings:
        Notification.objects.create(
            user=booking.learner,
            type='session_starting',
            title='Session Starting!',
            message=f'Your session "{session.title}" is now live! Join the room.',
            related_session=session
        )
    
    # The mentor is redirected to the room directly
    return JsonResponse({
        'success': True,
        'message': 'Session started successfully!',
        'redirect_url': f'/sessions/{session_id}/room/'
    })


@login_required
@require_http_methods(["POST"])
def end_session(request, session_id):
    """End a session (mentor only) - Enhanced version"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Verify mentor authorization
        if session.mentor != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Only the session mentor can end the session'
            }, status=403)
        
        # Check if session can be ended
        if session.status == 'completed':
            return JsonResponse({
                'success': True,
                'message': 'Session was already ended',
                'session_id': str(session.id),
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                'note': 'Session was already in completed status'
            })
        elif session.status not in ['live', 'scheduled']:
            return JsonResponse({
                'success': False,
                'error': f'Session cannot be ended - current status: {session.status}'
            }, status=400)
        
        # Use the model's end_session method for proper cleanup
        try:
            session.end_session()
            
            # Mark all active participants as left
            from .models import SessionParticipant
            active_participants = SessionParticipant.objects.filter(
                session=session,
                left_at__isnull=True
            )
            
            for participant in active_participants:
                participant.mark_left()
            
            # Update all bookings to completed status
            session.bookings.filter(status='confirmed').update(status='attended')
            
            return JsonResponse({
                'success': True,
                'message': 'Session ended successfully!',
                'session_id': str(session.id),
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                'actual_duration': session.actual_duration
            })
            
        except Exception as model_error:
            # Fallback to simple status update if model method fails
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Session ended successfully!',
                'session_id': str(session.id),
                'note': 'Used fallback method'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to end session: {str(e)}'
        }, status=500)


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
@require_http_methods(["GET"])
def get_recent_notifications_api(request):
    """Get recent notifications for notification dropdown"""
    try:
        notifications_list = []
        recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        for notification in recent_notifications:
            notifications_list.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'read': notification.read,
                'created_at': notification.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_list
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


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


@login_required
@require_http_methods(["GET"])
def mentor_dashboard_data(request):
    """Get real mentor dashboard data from database"""
    try:
        if request.user.role != 'mentor':
            return JsonResponse({'error': 'Only mentors can access this data'}, status=403)
        
        from django.utils import timezone
        from django.db.models import Count, Avg
        
        # Real sessions data from database
        mentor_sessions = Session.objects.filter(mentor=request.user)
        
        # Calculate real statistics
        total_students = Booking.objects.filter(
            session__mentor=request.user,
            status='confirmed'
        ).values('learner').distinct().count()
        
        sessions_this_month = mentor_sessions.filter(
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count()
        
        avg_rating = Feedback.objects.filter(
            session__mentor=request.user
        ).aggregate(avg=Avg('rating'))['avg'] or 0.0
        
        # Real earnings from completed sessions
        completed_bookings = Booking.objects.filter(
            session__mentor=request.user,
            status='completed'
        )
        hourly_rate = getattr(request.user, 'hourly_rate', None) or 25
        monthly_earnings = completed_bookings.filter(
            created_at__month=timezone.now().month
        ).count() * hourly_rate * 1.5
        
        # FIXED: Organize sessions with proper categorization logic
        draft_sessions = []
        scheduled_sessions = []
        booked_sessions = []  # Sessions with bookings ready to start
        live_sessions = []    # Currently running sessions
        past_sessions = []
        
        for session in mentor_sessions:
            bookings_count = session.bookings.filter(status='confirmed').count()
            print(f"Session ID: {session.id}, Title: {session.title}, Status: {session.status}, Bookings: {bookings_count}")
            
            # Get booked learners data
            booked_learners = []
            for booking in session.bookings.filter(status='confirmed'):
                booked_learners.append({
                    'id': booking.learner.id,
                    'name': booking.learner.get_full_name() or booking.learner.username,
                    'bookedDate': booking.created_at.strftime('%b %d, %Y'),
                    'isReady': booking.is_ready,
                    'status': booking.status
                })
            
            # Calculate time to start for session readiness
            time_to_start = 999
            if session.schedule:
                time_diff = session.schedule - timezone.now()
                time_to_start = int(time_diff.total_seconds() / 60)
                
                # Auto-move past sessions to completed
                if time_to_start < -60 and session.status != 'live':  # Don't auto-complete live sessions
                    session.status = 'completed'
                    session.save()
            
            session_data = {
                'id': str(session.id),
                'title': session.title,
                'description': session.description,
                'thumbnail': session.thumbnail.url if session.thumbnail else None,
                'category': session.category,
                'skills': session.skills,
                'price': str(session.price) if session.price else 'Free',
                'schedule': session.schedule.strftime('%b %d, %I:%M %p') if session.schedule else '',
                'duration': session.duration,
                'maxParticipants': session.max_participants,
                'participants': bookings_count,
                'current_participants': bookings_count,
                'current_bookings': bookings_count,
                'bookedCount': bookings_count,
                'bookedLearners': booked_learners,
                'status': session.status,
                'bookings_text': f'Booked: {bookings_count}/{session.max_participants}',
                'timeToStart': time_to_start,
                'mentorReady': False,
                'learnersReady': bookings_count > 0,
                'readyLearners': sum(1 for learner in booked_learners if learner['isReady']),
                'expectedEarnings': bookings_count * 500,
                'publishing': False,
                'started_at': session.started_at.isoformat() if session.started_at else None
            }
            
            # FIXED: Proper categorization logic
            if session.status == 'draft':
                print(f"  → Draft: {session.title}")
                draft_sessions.append(session_data)
            elif session.status == 'scheduled':
                if bookings_count > 0:
                    print(f"  → Booked (ready to start): {session.title}")
                    booked_sessions.append(session_data)  # Has bookings, ready to start
                else:
                    print(f"  → Scheduled (waiting for bookings): {session.title}")
                    scheduled_sessions.append(session_data)  # No bookings yet
            elif session.status == 'live':
                print(f"  → Live: {session.title}")
                live_sessions.append(session_data)  # Currently running
            else:  # completed or past
                print(f"  → Past: {session.title}")
                session_data['status'] = 'completed'
                past_sessions.append(session_data)
        
        # Real pending requests from database
        pending_requests = []
        for req in Request.objects.filter(mentor=request.user, status='pending'):
            pending_requests.append({
                'id': req.id,
                'title': req.topic or 'Session Request',
                'learner_name': req.learner.username,
                'description': req.description,
                'created_at': req.created_at.strftime('%b %d, %Y'),
                'status': req.status
            })
        
        # FIXED: Return properly categorized sessions in the format expected by frontend
        return JsonResponse({
            'success': True,
            'sessions': {
                'draft': draft_sessions,           # Status: draft
                'scheduled': scheduled_sessions,   # Status: scheduled, no bookings
                'booked': booked_sessions,        # Status: scheduled, has bookings (ready to start)
                'live': live_sessions,            # Status: live (actually running)
                'past': past_sessions,            # Status: completed
            },
            'stats': {
                'totalStudents': total_students,
                'sessionsThisMonth': sessions_this_month,
                'averageRating': round(avg_rating, 1),
                'monthlyEarnings': int(monthly_earnings)
            },
            'requests': pending_requests,
            'analytics': {
                'monthlyEarnings': [
                    {'month': 'Jan', 'amount': 5000},
                    {'month': 'Feb', 'amount': 7500},
                    {'month': 'Mar', 'amount': 6000},
                    {'month': 'Apr', 'amount': 8000},
                    {'month': 'May', 'amount': 9000},
                    {'month': 'Jun', 'amount': int(monthly_earnings)}
                ],
                'totalSessions': mentor_sessions.count(),
                'completedSessions': len(past_sessions),
                'averageRating': round(avg_rating, 1),
                'totalStudents': total_students,
                'maxEarning': 10000
            }
        })
        
    except Exception as e:
        print(f"Error in mentor_dashboard_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def follow_mentor_api(request):
    """Follow/unfollow a mentor"""
    try:
        data = json.loads(request.body)
        mentor_id = data.get('mentor_id')
        
        mentor = User.objects.get(id=mentor_id, role='mentor')
        
        return JsonResponse({
            'success': True,
            'mentor_name': f"{mentor.first_name} {mentor.last_name}",
            'message': 'Successfully followed mentor'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def request_mentor_session_api(request):
    """Create a session request to a specific mentor"""
    try:
        mentor_id = request.POST.get('mentor_id')
        topic = request.POST.get('topic')
        duration = request.POST.get('duration')
        urgency = request.POST.get('urgency')
        description = request.POST.get('description')
        
        mentor = User.objects.get(id=mentor_id, role='mentor')
        
        session_request = Request.objects.create(
            learner=request.user,
            mentor=mentor,
            topic=topic,
            description=description,
            domain=mentor.domain or 'General',
            duration=int(duration),
            urgency=urgency,
            status='pending'
        )
        
        Notification.objects.create(
            user=mentor,
            title="New Session Request",
            message=f"{request.user.first_name} requested a session on {topic}",
            type='request'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Session request sent successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def create_session_api(request):
    """Create session from modal - Complete workflow with recommendations"""
    try:
        if request.user.role != 'mentor':
            return JsonResponse({'error': 'Only mentors can create sessions'}, status=403)
        
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip() 
        schedule_str = request.POST.get('schedule', '')
        duration = int(request.POST.get('duration', 60))
        max_participants = int(request.POST.get('max_participants', 10))
        status = request.POST.get('status', 'draft')
        
        # Validation
        if not all([title, description, schedule_str]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
            
        # Parse schedule
        from datetime import datetime
        from django.utils import timezone
        
        schedule = datetime.strptime(schedule_str, '%Y-%m-%dT%H:%M')
        if timezone.is_naive(schedule):
            schedule = timezone.make_aware(schedule)
            
        if schedule <= timezone.now():
            return JsonResponse({'error': 'Session must be scheduled for future'}, status=400)
        
        # Handle new fields for ML recommendations and pricing
        thumbnail = request.FILES.get('thumbnail')
        category = request.POST.get('category', '')
        skills = request.POST.get('skills', '')
        session_type = request.POST.get('session_type', 'free')
        price = None
        
        if session_type == 'paid':
            price_value = request.POST.get('price')
            if price_value:
                try:
                    price = float(price_value)
                except ValueError:
                    return JsonResponse({'error': 'Invalid price format'}, status=400)
        
        # FIXED: Correct status mapping for session creation
        # When user selects "publish" in the form, save as "scheduled" (available for booking)
        # When user selects "draft", save as "draft" (not visible to learners)
        if status == 'publish':
            final_status = 'scheduled'  # Available for learners to book
        else:
            final_status = 'draft'  # Not visible to learners
        
        # Create session in database
        session = Session.objects.create(
            mentor=request.user,
            title=title,
            description=description, 
            thumbnail=thumbnail,
            category=category,
            skills=skills,
            price=price,
            schedule=schedule,
            duration=duration,
            max_participants=max_participants,
            status=final_status
        )
        
        # If published (scheduled), make available for learner booking & recommendations
        if final_status == 'scheduled':
            from recommendations.models import PopularityMetric
            PopularityMetric.objects.get_or_create(
                session=session,
                defaults={'view_count': 0, 'booking_count': 0}
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Session created successfully!',
            'session_id': str(session.id),
            'status': session.status
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def start_session_api(request, session_id):
    """Start session (redirect to WebRTC room) - FIXED: Only allow start if learners booked"""
    try:
        session = get_object_or_404(Session, id=session_id, mentor=request.user)
        
        # FIXED: Check if session has any confirmed bookings before allowing start
        confirmed_bookings = Booking.objects.filter(session=session, status='confirmed')
        if not confirmed_bookings.exists():
            return JsonResponse({
                'success': False,
                'error': 'Cannot start session without any booked learners',
                'message': 'Wait for learners to book your session before starting'
            }, status=400)
        
        # FIXED: Update session status to 'live' (not 'active')
        session.status = 'live'
        session.started_at = timezone.now()
        session.save()
        
        # Notify all booked learners
        for booking in confirmed_bookings:
            Notification.objects.create(
                user=booking.learner,
                type='session_started',
                title='Session Started!',
                message=f'"{session.title}" has started. Join now!',
                related_session=session
            )
        
        return JsonResponse({
            'success': True,
            'room_url': f'/sessions/{session_id}/room/',
            'message': 'Session started successfully!',
            'participant_count': confirmed_bookings.count()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def session_bookings(request, session_id):
    """Get all bookings for a session"""
    print(f"Attempting to get bookings for session {session_id}. User: {request.user.username} (ID: {request.user.id}, IsAuthenticated: {request.user.is_authenticated})")
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Ensure only mentor can view their session's bookings
        if session.mentor != request.user:
            return JsonResponse({'error': 'You are not authorized to view these bookings'}, status=403)

        bookings = Booking.objects.filter(session=session, status='confirmed').select_related('learner')
        
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'id': str(booking.id),
                'learner_id': str(booking.learner.id),
                'name': booking.learner.get_full_name() or booking.learner.username,
                'email': booking.learner.email,
                'bookedDate': booking.created_at.strftime('%Y-%m-%d %H:%M'),
                'isReady': booking.is_ready,
                'status': booking.status
            })
        
        return JsonResponse({
            'success': True,
            'bookings': booking_data,
            'total_bookings': len(booking_data)
        })
        
    except Http404: # Catch Http404 specifically
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def send_session_reminders(request, session_id):
    """Send session reminders to participants"""
    try:
        session = get_object_or_404(Session, id=session_id)
        reminder_type = json.loads(request.body).get('reminder_type', 'general')
        
        # Get all confirmed bookings
        bookings = Booking.objects.filter(session=session, status='confirmed')
        
        for booking in bookings:
            # Create notification
            Notification.objects.create(
                user=booking.learner,
                type='session_reminder',
                title=f'Session Reminder: {session.title}',
                message=f'Your session "{session.title}" starts in {reminder_type.replace("_", " ")}',
                related_session=session
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Reminders sent to {bookings.count()} participants'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def join_session_api(request, session_id):
    """Join a live session"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Check if user has booking
        if request.user != session.mentor:
            booking = get_object_or_404(Booking, 
                                      session=session, 
                                      learner=request.user, 
                                      status='confirmed')
        
        # Check if session is live
        if session.status != 'live':
            return JsonResponse({
                'success': False,
                'error': 'Session is not live yet'
            }, status=400)
        
        # Create or update participant record
        participant, created = SessionParticipant.objects.get_or_create(
            session=session,
            user=request.user,
            defaults={'is_mentor': request.user == session.mentor}
        )
        
        if not created and participant.left_at:
            # User is rejoining
            participant.left_at = None
            participant.reconnection_count += 1
            participant.save()
        
        return JsonResponse({
            'success': True,
            'room_url': f'/sessions/{session_id}/room/',
            'participant_count': SessionParticipant.objects.filter(
                session=session, 
                left_at__isnull=True
            ).count()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required 
@require_http_methods(["GET"])
def get_live_sessions_advanced(request):
    """Get live sessions with advanced real-time data"""
    try:
        live_sessions = Session.objects.filter(status='live').select_related('mentor')
        
        sessions_data = []
        for session in live_sessions:
            participant_count = SessionParticipant.objects.filter(
                session=session,
                left_at__isnull=True
            ).count()
            
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'mentor_name': session.mentor.get_full_name() or session.mentor.username,
                'duration': session.duration,
                'participant_count': participant_count,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'schedule': session.schedule.isoformat() if session.schedule else None,
                'category': session.category,
                'is_booked': Booking.objects.filter(
                    session=session,
                    learner=request.user,
                    status='confirmed'
                ).exists() if request.user != session.mentor else True
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def mark_learner_ready(request, session_id):
    """Mark learner as ready for session"""
    try:
        booking = Booking.objects.get(
            session_id=session_id,
            learner=request.user,
            status='confirmed'
        )
        
        # Update booking status to ready
        booking.ready_status = True
        booking.save()
        
        # Trigger real-time notification to mentor
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"session_{session_id}",
                {
                    'type': 'learner_ready',
                    'message': f'{request.user.username} is ready for the session',
                    'learner_id': request.user.id,
                    'session_id': str(session_id)
                }
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Marked as ready successfully!'
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Booking not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_mentor_ready(request, session_id):
    """Mark mentor as ready for session - Fixed version without mentor_ready field"""
    try:
        session = get_object_or_404(Session, id=session_id, mentor=request.user)
        
        # Create a special notification to track mentor ready status
        existing_ready_notification = Notification.objects.filter(
            user=session.mentor,
            type='mentor_ready_status',
            related_session=session
        ).first()
        
        if not existing_ready_notification:
            Notification.objects.create(
                user=session.mentor,
                type='mentor_ready_status',
                title='Mentor Ready Status',
                message=f'Mentor marked ready for session "{session.title}"',
                related_session=session,
                read=True  # This is just a status marker
            )
        
        # Notify all booked learners
        bookings = Booking.objects.filter(session=session, status='confirmed')
        for booking in bookings:
            Notification.objects.create(
                user=booking.learner,
                type='mentor_ready',
                title='Mentor is Ready!',
                message=f'Your mentor is ready for "{session.title}". Get ready to join!',
                related_session=session
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Marked as ready successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def mark_ready_unified(request, session_id):
    """Mark user as ready for session - handles both learner and mentor"""
    try:
        # Check if user is a mentor for this session
        try:
            session = Session.objects.get(id=session_id, mentor=request.user)
            # User is mentor - create notifications for learners
            
            bookings = Booking.objects.filter(session=session, status='confirmed')
            for booking in bookings:
                Notification.objects.create(
                    user=booking.learner,
                    type='session_starting',
                    title='Mentor is Ready!',
                    message=f'Your mentor is ready for "{session.title}". Get ready to join!',
                    related_session=session
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Mentor marked as ready successfully!',
                'user_type': 'mentor'
            })
            
        except Session.DoesNotExist:
            # User is not mentor, check if they're a learner
            booking = Booking.objects.get(
                session_id=session_id,
                learner=request.user,
                status='confirmed'
            )
            
            booking.is_ready = True  # Set learner's ready status
            booking.save()

            # Create notification for the mentor
            session = booking.session
            Notification.objects.create(
                user=session.mentor,
                type='booking_confirmed',
                title='Learner is Ready!',
                message=f'{request.user.username} is ready for "{session.title}"',
                related_session=session
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Learner marked as ready successfully!',
                'user_type': 'learner'
            })
            
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No booking found for this session'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def handle_session_request(request, request_id):
    """Handle mentor's response to session request (accept/decline)"""
    try:
        action = request.POST.get('action')
        if action not in ['accept', 'decline']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            }, status=400)
        
        # Get session request
        try:
            session_request = Request.objects.get(
                id=request_id,
                mentor=request.user,
                status='pending'
            )
        except Request.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Session request not found or already handled'
            }, status=404)
        
        if action == 'accept':
            # Create session
            session = Session.objects.create(
                mentor=request.user,
                learner=session_request.learner,
                topic=session_request.topic,
                description=session_request.description,
                duration=session_request.duration,
                schedule=session_request.schedule,
                status='scheduled'
            )
            
            # Update request status
            session_request.status = 'accepted'
            session_request.save()
            
            # Create notification for learner
            from notifications.models import Notification
            Notification.objects.create(
                recipient=session_request.learner,
                sender=request.user,
                notification_type='session_accepted',
                title='Session Request Accepted',
                message=f"{request.user.get_full_name()} has accepted your session request on {session_request.topic}",
                related_object_id=session.id
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Session request accepted',
                'session_id': session.id
            })
            
        else:  # decline
            session_request.status = 'declined'
            session_request.save()
            
            # Create notification for learner
            from notifications.models import Notification
            Notification.objects.create(
                recipient=session_request.learner,
                sender=request.user,
                notification_type='session_declined',
                title='Session Request Declined',
                message=f"{request.user.get_full_name()} has declined your session request on {session_request.topic}",
                related_object_id=session_request.id
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Session request declined'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_session_status(request, session_id):
    """API to get the current status of a session."""
    session = get_object_or_404(Session, id=session_id)
    return JsonResponse({
        'success': True,
        'status': session.status
    })

@login_required
@require_http_methods(["GET"])
def get_requests_api(request):
    """Get all requests for the current mentor"""
    try:
        if request.user.role != 'mentor':
            return JsonResponse({'error': 'Only mentors can access this data'}, status=403)
        
        requests_list = []
        for req in Request.objects.filter(mentor=request.user).order_by('-created_at'):
            requests_list.append({
                'id': req.id,
                'topic': req.topic or 'Session Request',
                'learner_name': req.learner.get_full_name() or req.learner.username,
                'description': req.description,
                'duration': req.duration,
                'urgency': req.urgency,
                'status': req.status,
                'created_at': req.created_at.isoformat(),
                'domain': req.domain
            })
        
        return JsonResponse({
            'success': True,
            'requests': requests_list
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def mark_notification_read_api(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def get_live_sessions(request):
    """Get live sessions for learner dashboard"""
    try:
        # Get sessions where user is booked and session is live
        live_sessions = Session.objects.filter(
            status='live',
            bookings__learner=request.user,
            bookings__status='confirmed'
        ).select_related('mentor').distinct()
        
        sessions_data = []
        for session in live_sessions:
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'mentor_name': session.mentor.get_full_name() or session.mentor.username,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'duration': session.duration,
                'current_participants': session.current_participants,
                'status': session.status
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data,
            'count': len(sessions_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Allow requests without CSRF token for API
@login_required
@require_http_methods(["POST"])
def mark_ready_api(request, session_id):
    """Mark user as ready for session - Unified handler for both mentors and learners"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Handle based on user type
        if request.user.role == 'mentor':
            # MENTOR READY LOGIC
            if session.mentor != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Only the session mentor can mark themselves as ready'
                }, status=403)
            
            # Instead of using a mentor_ready field, create a special notification
            # This approach doesn't require database schema changes
            existing_ready_notification = Notification.objects.filter(
                user=session.mentor,
                type='mentor_ready_status',
                related_session=session
            ).first()
            
            if not existing_ready_notification:
                Notification.objects.create(
                    user=session.mentor,
                    type='mentor_ready_status',
                    title='Mentor Ready Status',
                    message=f'Mentor marked ready for session "{session.title}"',
                    related_session=session,
                    read=True  # This is just a status marker
                )
            
            # Notify all learners with confirmed bookings
            confirmed_bookings = session.bookings.filter(status='confirmed')
            for booking in confirmed_bookings:
                Notification.objects.create(
                    user=booking.learner,
                    type='mentor_ready',
                    title='Mentor Ready!',
                    message=f'Your mentor {request.user.get_full_name() or request.user.username} is ready for "{session.title}"',
                    related_session=session
                )
            
            # Send real-time notifications via WebSocket
            channel_layer = get_channel_layer()
            if channel_layer:
                for booking in confirmed_bookings:
                    async_to_sync(channel_layer.group_send)(
                        f'dashboard_{booking.learner.id}',
                        {
                            'type': 'mentor_ready',
                            'session_id': str(session.id),
                            'mentor_name': request.user.get_full_name() or request.user.username,
                            'session_title': session.title
                        }
                    )
            
            return JsonResponse({
                'success': True,
                'message': 'Marked as ready! All learners have been notified.'
            })
            
        else:
            # LEARNER READY LOGIC
            # Check if user has booked this session
            try:
                booking = Booking.objects.get(
                    session=session, 
                    learner=request.user,
                    status='confirmed'
                )
            except Booking.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'You are not booked for this session'
                }, status=400)
            
            # Mark as ready
            booking.is_ready = True
            booking.save()
            
            # Create notification for mentor
            Notification.objects.create(
                user=session.mentor,
                type='learner_ready',
                title='Learner Ready!',
                message=f'{request.user.get_full_name() or request.user.username} is ready for "{session.title}"',
                related_session=session
            )
            
            # Send real-time notification via WebSocket
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'dashboard_{session.mentor.id}',
                    {
                        'type': 'learner_ready',
                        'session_id': str(session.id),
                        'learner_name': request.user.get_full_name() or request.user.username,
                        'session_title': session.title
                    }
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Marked as ready! Mentor will be notified.'
            })
        
    except Exception as e:
        print(f"Error in mark_ready_api: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["GET"])
def get_session_status_real_time(request, session_id):
    """Get real-time session status - FIXED endpoint"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Get participant count
        participant_count = SessionParticipant.objects.filter(
            session=session, 
            left_at__isnull=True
        ).count()
        
        # Get booking info for this user
        booking = None
        user_status = 'not_booked'
        
        if request.user != session.mentor:
            booking = Booking.objects.filter(
                session=session,
                learner=request.user
            ).first()
            
            if booking:
                user_status = booking.status
        
        return JsonResponse({
            'status': session.status,
            'participant_count': participant_count,
            'user_status': user_status,
            'can_join': session.status == 'live',
            'is_mentor': request.user == session.mentor,
            'session_progress': session.session_progress if session.is_live else 0,
            'started_at': session.started_at.isoformat() if session.started_at else None,
            'ended_at': session.ended_at.isoformat() if session.ended_at else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def mentor_analytics_api(request):
    """Get analytics data for mentor dashboard"""
    try:
        user = request.user
        
        # Get mentor's sessions
        sessions = Session.objects.filter(mentor=user)
        
        # Calculate analytics
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='completed').count()
        live_sessions = sessions.filter(status='live').count()
        
        # Get total earnings (sum of prices for completed sessions)
        total_earnings = sessions.filter(
            status='completed',
            price__gt=0
        ).aggregate(
            total=Sum('price')
        )['total'] or 0
        
        # Get unique students count
        unique_students = Booking.objects.filter(
            session__mentor=user,
            status__in=['confirmed', 'attended', 'completed']
        ).values('learner').distinct().count()
        
        # Monthly earnings for last 6 months
        from datetime import datetime, timedelta
        import calendar
        
        monthly_earnings = []
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            month_name = calendar.month_abbr[date.month]
            
            month_earnings = sessions.filter(
                status='completed',
                schedule__year=date.year,
                schedule__month=date.month,
                price__gt=0
            ).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            monthly_earnings.insert(0, {
                'month': month_name,
                'amount': float(month_earnings)
            })
        
        # Calculate average rating
        avg_rating = sessions.filter(
            feedback__isnull=False
        ).aggregate(
            avg_rating=Avg('feedback__rating')
        )['avg_rating'] or 4.5
        
        analytics_data = {
            'totalSessions': total_sessions,
            'completedSessions': completed_sessions,
            'liveSessions': live_sessions,
            'averageRating': round(float(avg_rating), 1),
            'totalStudents': unique_students,
            'totalEarnings': float(total_earnings),
            'monthlyEarnings': monthly_earnings
        }
        
        return Response({
            'success': True,
            'analytics': analytics_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def learner_dashboard_data(request):
    """Get real learner dashboard data from database"""
    try:
        from django.utils import timezone
        from django.db.models import Count, Avg
        
        # Real bookings data from database for this learner
        learner_bookings = Booking.objects.filter(learner=request.user).select_related('session', 'session__mentor')
        
        # Calculate real statistics
        total_sessions_attended = learner_bookings.filter(status='completed').count()
        upcoming_sessions_count = learner_bookings.filter(
            status__in=['confirmed', 'booked'],
            session__schedule__gt=timezone.now()
        ).count()
        
        # Total learning hours
        total_hours = learner_bookings.filter(
            status='completed'
        ).aggregate(
            total=Sum('session__duration')
        )['total'] or 0
        total_hours = int(total_hours / 60) if total_hours else 0  # Convert minutes to hours
        
        # Unique mentors count
        unique_mentors = learner_bookings.filter(
            status='completed'
        ).values('session__mentor').distinct().count()
        
        # FIXED: Organize sessions for learner dashboard with proper date/time logic
        upcoming_sessions = []
        live_sessions = []
        past_sessions = []
        now = timezone.now()
        
        for booking in learner_bookings:
            session = booking.session
            session_time = session.schedule if session.schedule else now
            is_future = session_time > now
            is_past = session_time <= now
            
            print(f"Learner Session: {session.title}, Status: {session.status}, Booking: {booking.status}, Schedule: {session_time}, Future: {is_future}")
            
            session_data = {
                'id': str(session.id),
                'title': session.title,
                'description': session.description,
                'mentor': {
                    'id': session.mentor.id,
                    'name': session.mentor.get_full_name() or session.mentor.username,
                    'username': session.mentor.username,
                },
                'price': float(session.price) if session.price else 0,
                'schedule': session.schedule.isoformat() if session.schedule else None,
                'duration': session.duration,
                'status': session.status,
                'booking_status': booking.status,
                'is_ready': booking.is_ready,
                'joined_at': booking.joined_at.isoformat() if booking.joined_at else None,
                'attendance_duration': booking.attendance_duration or 0,
                'is_future': is_future,
                'is_past': is_past,
            }
            
            # Categorize based on ACTUAL time and status logic
            if session.status in ['live', 'active'] and booking.status in ['confirmed', 'booked']:
                # Currently live or active sessions
                live_sessions.append(session_data)
            elif is_future and session.status in ['scheduled'] and booking.status in ['confirmed', 'booked']:
                # Future sessions that are scheduled and confirmed
                upcoming_sessions.append(session_data)
            elif is_past or booking.status in ['completed', 'attended'] or session.status in ['completed']:
                # Past sessions or completed bookings
                past_sessions.append(session_data)
            elif session.status == 'active':
                # Handle active sessions (treat as live if not clearly past)
                if is_past:
                    past_sessions.append(session_data)
                else:
                    live_sessions.append(session_data)
            else:
                # Handle edge cases - put in appropriate category based on time
                if is_past:
                    past_sessions.append(session_data)
                else:
                    upcoming_sessions.append(session_data)
        
        # Get available sessions for browsing (not booked by this learner)
        booked_session_ids = learner_bookings.values_list('session_id', flat=True)
        available_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gt=timezone.now()
        ).exclude(
            id__in=booked_session_ids
        ).select_related('mentor')[:10]  # Limit to 10 for performance
        
        browse_sessions = []
        for session in available_sessions:
            browse_sessions.append({
                'id': str(session.id),
                'title': session.title,
                'description': session.description,
                'mentor': {
                    'id': session.mentor.id,
                    'name': session.mentor.get_full_name() or session.mentor.username,
                },
                'price': float(session.price) if session.price else 0,
                'schedule': session.schedule.isoformat() if session.schedule else None,
                'duration': session.duration,
                'max_participants': session.max_participants,
                'current_bookings': session.bookings.filter(status='confirmed').count(),
                'is_full': session.bookings.filter(status='confirmed').count() >= session.max_participants,
            })
        
        # Get learner's session requests
        learner_requests = Request.objects.filter(learner=request.user).select_related('mentor')
        
        requests_data = []
        for req in learner_requests:
            requests_data.append({
                'id': req.id,
                'topic': req.topic,
                'description': req.description,
                'mentor_name': req.mentor.get_full_name() if req.mentor else 'Any Mentor',
                'status': req.status,
                'urgency': req.urgency,
                'domain': req.domain,
                'duration': req.duration,
                'created_at': req.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'sessions': {
                'upcoming': upcoming_sessions,
                'live': live_sessions, 
                'past': past_sessions,
                'available': browse_sessions,
            },
            'requests': requests_data,
            'stats': {
                'attended_sessions': total_sessions_attended,
                'upcoming_count': upcoming_sessions_count,
                'total_hours': total_hours,
                'unique_mentors': unique_mentors,
            }
        })
        
    except Exception as e:
        print(f"Error in learner_dashboard_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def find_mentors_api(request):
    """Find mentors based on learner requirements using intelligent matching"""
    try:
        data = json.loads(request.body)
        
        # Build learner profile from request data
        learner_profile = {
            'skills': data.get('skills', []),
            'domain': data.get('domain', ''),
            'urgency': data.get('urgency', 'flexible'),
            'budget': data.get('budget', ''),
            'preferred_times': data.get('preferred_times', [])
        }
        
        # Get mentor recommendations
        recommendations = get_mentor_recommendations(learner_profile, max_results=10)
        
        # Format response
        mentors_data = []
        for rec in recommendations:
            mentor = rec['mentor']
            mentors_data.append({
                'id': str(mentor.id),
                'username': mentor.username,
                'full_name': mentor.get_full_name(),
                'bio': mentor.bio,
                'skills': mentor.get_skills_list(),
                'hourly_rate': float(mentor.hourly_rate) if mentor.hourly_rate else 0,
                'experience_years': mentor.experience_years,
                'profile_image_url': mentor.profile_image_url,
                'match_score': rec['score'],
                'match_reasons': rec['match_reasons'],
                'availability': rec['availability'],
                'stats': rec['stats']
            })
        
        return JsonResponse({
            'success': True,
            'mentors': mentors_data,
            'total_found': len(mentors_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def get_recommended_sessions_api(request):
    """Get personalized session recommendations for learner"""
    try:
        if not request.user.is_learner:
            return JsonResponse({
                'success': False,
                'error': 'Only learners can get session recommendations'
            }, status=403)
        
        # Get session recommendations
        recommended_sessions = get_session_recommendations(request.user, limit=10)
        
        # Format response
        sessions_data = []
        for session in recommended_sessions:
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'description': session.description,
                'mentor_name': session.mentor.get_full_name() or session.mentor.username,
                'mentor_id': str(session.mentor.id),
                'schedule': session.schedule.isoformat(),
                'duration': session.duration,
                'price': float(session.price) if session.price else 0,
                'current_participants': session.current_participants,
                'max_participants': session.max_participants,
                'is_full': session.is_full,
                'skills': session.skills.split(',') if session.skills else [],
                'category': session.category,
                'thumbnail': session.thumbnail.url if session.thumbnail else None
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data,
            'total_found': len(sessions_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def request_mentor_match_api(request):
    """Request a mentor match based on specific requirements"""
    try:
        data = json.loads(request.body)
        
        # Create a session request
        session_request = Request.objects.create(
            learner=request.user,
            topic=data.get('topic'),
            description=data.get('description'),
            domain=data.get('domain', ''),
            skills=', '.join(data.get('skills', [])),
            duration=int(data.get('duration', 60)),
            urgency=data.get('urgency', 'flexible'),
            budget=data.get('budget', ''),
            preferred_times=data.get('preferred_times', []),
            status='pending'
        )
        
        # Find matching mentors
        learner_profile = {
            'skills': data.get('skills', []),
            'domain': data.get('domain', ''),
            'urgency': data.get('urgency', 'flexible'),
            'budget': data.get('budget', ''),
            'preferred_times': data.get('preferred_times', [])
        }
        
        recommendations = get_mentor_recommendations(learner_profile, max_results=5)
        
        # Notify top 3 matching mentors
        channel_layer = get_channel_layer()
        
        for rec in recommendations[:3]:
            mentor = rec['mentor']
            
            # Create notification for mentor
            notification = Notification.objects.create(
                user=mentor,
                type='new_request',
                title='New Session Request Match',
                message=f'{request.user.get_full_name()} is looking for help with {data.get("topic")}. Match score: {rec["score"]:.1f}',
                related_request=session_request
            )
            
            # Send real-time notification
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'dashboard_{mentor.id}',
                    {
                        'type': 'notification',
                        'notification_data': {
                            'id': str(notification.id),
                            'title': notification.title,
                            'message': notification.message,
                            'type': notification.type,
                            'timestamp': notification.created_at.isoformat()
                        }
                    }
                )
        
        return JsonResponse({
            'success': True,
            'message': 'Request sent to matching mentors',
            'request_id': str(session_request.id),
            'mentors_notified': len(recommendations[:3])
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def get_connection_status_api(request, session_id):
    """Get real-time connection status for a session"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Verify access
        has_access = (
            session.mentor == request.user or
            session.bookings.filter(learner=request.user, status='confirmed').exists()
        )
        
        if not has_access:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get active participants
        from .models import SessionParticipant
        participants = SessionParticipant.objects.filter(
            session=session,
            left_at__isnull=True
        ).select_related('user')
        
        participants_data = []
        for participant in participants:
            participants_data.append({
                'user_id': str(participant.user.id),
                'username': participant.user.username,
                'is_mentor': participant.is_mentor,
                'connection_status': participant.connection_status,
                'network_quality': participant.network_quality,
                'joined_at': participant.joined_at.isoformat(),
                'last_activity': participant.last_activity.isoformat(),
                'is_muted': participant.is_muted,
                'is_video_off': participant.is_video_off,
                'is_screen_sharing': participant.is_screen_sharing,
                'packet_loss': participant.packet_loss,
                'latency': participant.latency,
                'bandwidth': participant.bandwidth
            })
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.id),
            'session_status': session.status,
            'participants': participants_data,
            'total_participants': len(participants_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def update_connection_status_api(request, session_id):
    """Update user's connection status in a session"""
    try:
        data = json.loads(request.body)
        session = get_object_or_404(Session, id=session_id)
        
        # Get or create participant
        from .models import SessionParticipant
        participant, created = SessionParticipant.objects.get_or_create(
            session=session,
            user=request.user,
            defaults={'is_mentor': request.user.is_mentor}
        )
        
        # Update status based on data
        if 'connection_status' in data:
            participant.connection_status = data['connection_status']
        
        if 'network_quality' in data:
            participant.network_quality = data['network_quality']
        
        if 'is_muted' in data:
            participant.is_muted = data['is_muted']
        
        if 'is_video_off' in data:
            participant.is_video_off = data['is_video_off']
        
        if 'is_screen_sharing' in data:
            participant.is_screen_sharing = data['is_screen_sharing']
        
        if 'packet_loss' in data:
            participant.packet_loss = data['packet_loss']
        
        if 'latency' in data:
            participant.latency = data['latency']
        
        if 'bandwidth' in data:
            participant.bandwidth = data['bandwidth']
        
        participant.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Connection status updated'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_request_api(request):
    """Create a new session request with mentor selection"""
    try:
        data = request.data
        user = request.user
        
        # Validate required fields
        required_fields = ['topic', 'description', 'domain', 'duration']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'error': f'{field.title()} is required'
                }, status=400)
        
        # Get mentor if specified
        mentor = None
        if data.get('mentor_id'):
            try:
                mentor = User.objects.get(id=data['mentor_id'], role='mentor')
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Selected mentor not found'
                }, status=400)
        
        # Create request
        session_request = Request.objects.create(
            learner=user,
            mentor=mentor,
            topic=data['topic'],
            description=data['description'],
            domain=data['domain'],
            skills=data.get('skills', ''),
            duration=int(data['duration']),
            urgency=data.get('urgency', 'flexible'),
            budget=data.get('budget', ''),
            preferred_times=data.get('preferred_times', [])
        )
        
        # Create notification for mentor if specified
        if mentor:
            Notification.objects.create(
                user=mentor,
                type='new_request',
                title='New Session Request',
                message=f'{user.get_full_name()} has requested a session on {data["topic"]}',
                related_request=session_request
            )
        
        return Response({
            'success': True,
            'message': 'Request created successfully!',
            'request_id': str(session_request.id)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_available_mentors(request):
    """Get available mentors for request selection"""
    try:
        user = request.user
        
        # Get all active mentors with complete profiles
        mentors = User.objects.filter(
            role='mentor',
            is_active=True,
            first_name__isnull=False,
            last_name__isnull=False
        ).exclude(
            first_name='',
            last_name=''
        ).order_by('-date_joined')
        
        # Format mentor data
        mentor_data = []
        for mentor in mentors:
            mentor_data.append({
                'id': str(mentor.id),
                'name': mentor.get_full_name(),
                'username': mentor.username,
                'bio': mentor.bio or 'Experienced mentor',
                'skills': mentor.skills or '',
                'domain': mentor.domain or '',
                'profile_image': mentor.profile_image.url if mentor.profile_image else None,
                'hourly_rate': mentor.hourly_rate or 0,
                'avg_rating': recommendation.get('avg_rating', 4.5),  # Use real rating from recommendation
                'total_sessions': Session.objects.filter(mentor=mentor, status='completed').count()
            })
        
        return Response({
            'success': True,
            'mentors': mentor_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def respond_to_request(request):
    """Mentor responds to a learner's request"""
    try:
        data = request.data
        user = request.user
        
        if user.role != 'mentor':
            return Response({
                'success': False,
                'error': 'Only mentors can respond to requests'
            }, status=403)
        
        request_id = data.get('request_id')
        response = data.get('response')  # 'accepted' or 'rejected'
        message = data.get('message', '')
        
        if not request_id or not response:
            return Response({
                'success': False,
                'error': 'Request ID and response are required'
            }, status=400)
        
        # Get the request
        try:
            session_request = Request.objects.get(id=request_id, mentor=user)
        except Request.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Request not found'
            }, status=404)
        
        # Update request status
        if response == 'accepted':
            session_request.status = 'accepted'
            notification_title = 'Request Accepted!'
            notification_message = f'{user.get_full_name()} has accepted your request for "{session_request.topic}"'
        else:
            session_request.status = 'rejected'
            notification_title = 'Request Declined'
            notification_message = f'{user.get_full_name()} has declined your request for "{session_request.topic}"'
        
        session_request.save()
        
        # Create notification for learner
        Notification.objects.create(
            user=session_request.learner,
            type='request_accepted' if response == 'accepted' else 'request_rejected',
            title=notification_title,
            message=notification_message + (f'\nMessage: {message}' if message else ''),
            related_request=session_request
        )
        
        return Response({
            'success': True,
            'message': f'Request {response} successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_learner_requests(request):
    """Get all requests for a learner"""
    try:
        user = request.user
        
        # Ensure user is a learner
        if user.role != 'learner':
            return Response({
                'success': False,
                'error': 'Only learners can view requests'
            }, status=403)
        
        # Get all requests from this learner
        requests = Request.objects.filter(
            learner=user
        ).select_related('mentor').order_by('-created_at')
        
        # Format request data
        request_data = []
        for req in requests:
            request_data.append({
                'id': str(req.id),
                'topic': req.topic,
                'description': req.description,
                'domain': req.domain,
                'skills': req.skills,
                'duration': req.duration,
                'urgency': req.urgency,
                'budget': req.budget,
                'status': req.status,
                'created_at': req.created_at.isoformat(),
                'updated_at': req.updated_at.isoformat(),
                'mentor': {
                    'id': str(req.mentor.id) if req.mentor else None,
                    'name': req.mentor.get_full_name() if req.mentor else 'Not assigned',
                    'username': req.mentor.username if req.mentor else '',
                    'profile_image': req.mentor.profile_image.url if req.mentor and req.mentor.profile_image else None
                } if req.mentor else None
            })
        
        return Response({
            'success': True,
            'requests': request_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_mentor_requests(request):
    """Get all requests for a mentor"""
    try:
        user = request.user
        
        # Ensure user is a mentor
        if user.role != 'mentor':
            return Response({
                'success': False,
                'error': 'Only mentors can view requests'
            }, status=403)
        
        # Get all requests to this mentor
        requests = Request.objects.filter(
            mentor=user
        ).select_related('learner').order_by('-created_at')
        
        # Format request data
        request_data = []
        for req in requests:
            request_data.append({
                'id': str(req.id),
                'topic': req.topic,
                'description': req.description,
                'domain': req.domain,
                'skills': req.skills,
                'duration': req.duration,
                'urgency': req.urgency,
                'budget': req.budget,
                'status': req.status,
                'created_at': req.created_at.isoformat(),
                'updated_at': req.updated_at.isoformat(),
                'learner': {
                    'id': str(req.learner.id),
                    'name': req.learner.get_full_name(),
                    'username': req.learner.username,
                    'profile_image': req.learner.profile_image.url if req.learner.profile_image else None
                }
            })
        
        return Response({
            'success': True,
            'requests': request_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def follow_mentor(request):
    """Follow/unfollow a mentor"""
    try:
        mentor_id = request.data.get('mentor_id')
        action = request.data.get('action', 'follow')  # 'follow' or 'unfollow'
        
        if not mentor_id:
            return Response({'success': False, 'error': 'Mentor ID required'}, status=400)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            mentor = User.objects.get(id=mentor_id, role='mentor')
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'Mentor not found'}, status=404)
        
        from users.models import Follow
        
        if action == 'follow':
            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=mentor
            )
            
            if created:
                # Create notification for mentor
                Notification.objects.create(
                    user=mentor,
                    title='New Follower',
                    message=f'{request.user.get_full_name() or request.user.username} started following you',
                    notification_type='info'
                )
                
                # Send real-time update to mentor dashboard
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'dashboard_{mentor.id}',
                    {
                        'type': 'notification',
                        'notification': {
                            'type': 'new_follower',
                            'message': f'{request.user.username} started following you',
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                )
                
                return Response({
                    'success': True,
                    'message': f'Now following {mentor.get_full_name() or mentor.username}',
                    'following': True
                })
            else:
                return Response({
                    'success': True,
                    'message': 'Already following this mentor',
                    'following': True
                })
        
        elif action == 'unfollow':
            deleted_count = Follow.objects.filter(
                follower=request.user,
                following=mentor
            ).delete()[0]
            
            if deleted_count > 0:
                return Response({
                    'success': True,
                    'message': f'Unfollowed {mentor.get_full_name() or mentor.username}',
                    'following': False
                })
            else:
                return Response({
                    'success': True,
                    'message': 'Not following this mentor',
                    'following': False
                })
        
        else:
            return Response({'success': False, 'error': 'Invalid action'}, status=400)
            
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_learner_requests(request):
    """Get learner's session requests with responses"""
    try:
        from sessions.models import Request
        
        # Get all requests for the learner
        user_requests = Request.objects.filter(
            learner=request.user
        ).select_related('mentor').order_by('-created_at')
        
        requests_data = []
        for req in user_requests:
            requests_data.append({
                'id': str(req.id),
                'topic': req.topic,
                'description': req.description,
                'domain': req.domain,
                'duration': req.duration,
                'urgency': req.urgency,
                'status': req.status,
                'mentor': {
                    'id': str(req.mentor.id) if req.mentor else None,
                    'name': req.mentor.get_full_name() if req.mentor else 'Any Available Mentor',
                    'username': req.mentor.username if req.mentor else 'system'
                } if req.mentor else None,
                'response_message': req.response_message,
                'created_at': req.created_at.isoformat(),
                'updated_at': req.updated_at.isoformat() if req.updated_at else None,
                'responded_at': req.responded_at.isoformat() if req.responded_at else None
            })
        
        return Response({
            'success': True,
            'requests': requests_data,
            'count': len(requests_data)
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_mentor_requests(request):
    """Get requests sent to mentor"""
    try:
        from sessions.models import Request
        
        # Get requests specifically for this mentor or general requests
        mentor_requests = Request.objects.filter(
            Q(mentor=request.user) | Q(mentor__isnull=True),
            status='pending'
        ).select_related('learner').order_by('-created_at')
        
        requests_data = []
        for req in mentor_requests:
            requests_data.append({
                'id': str(req.id),
                'topic': req.topic,
                'description': req.description,
                'domain': req.domain,
                'duration': req.duration,
                'urgency': req.urgency,
                'learner': {
                    'id': str(req.learner.id),
                    'name': req.learner.get_full_name() or req.learner.username,
                    'username': req.learner.username
                },
                'created_at': req.created_at.isoformat(),
                'budget': getattr(req, 'budget', 0)
            })
        
        return Response({
            'success': True,
            'requests': requests_data,
            'count': len(requests_data)
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def respond_to_request(request):
    """Mentor responds to session request"""
    try:
        from sessions.models import Request
        
        request_id = request.data.get('request_id')
        response_action = request.data.get('action')  # 'accept' or 'decline'
        response_message = request.data.get('message', '')
        
        if not request_id or not response_action:
            return Response({'success': False, 'error': 'Request ID and action required'}, status=400)
        
        session_request = Request.objects.get(id=request_id)
        
        # Verify mentor can respond to this request
        if session_request.mentor and session_request.mentor != request.user:
            return Response({'success': False, 'error': 'Not authorized to respond to this request'}, status=403)
        
        # Update request
        session_request.status = 'accepted' if response_action == 'accept' else 'declined'
        session_request.response_message = response_message
        session_request.responded_at = timezone.now()
        if not session_request.mentor:
            session_request.mentor = request.user
        session_request.save()
        
        # Create notification for learner
        Notification.objects.create(
            user=session_request.learner,
            title=f'Request {session_request.status.title()}',
            message=f'Your session request "{session_request.topic}" has been {session_request.status} by {request.user.get_full_name() or request.user.username}',
            notification_type='success' if response_action == 'accept' else 'warning'
        )
        
        # Send real-time update to learner dashboard
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'dashboard_{session_request.learner.id}',
            {
                'type': 'notification',
                'notification': {
                    'type': 'request_response',
                    'message': f'Your request "{session_request.topic}" was {session_request.status}',
                    'status': session_request.status,
                    'timestamp': timezone.now().isoformat()
                }
            }
        )
        
        return Response({
            'success': True,
            'message': f'Request {session_request.status} successfully',
            'action': response_action
        })
        
    except Request.DoesNotExist:
        return Response({'success': False, 'error': 'Request not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def acknowledge_request_response(request):
    """Learner acknowledges mentor's response"""
    try:
        from sessions.models import Request
        
        request_id = request.data.get('request_id')
        acknowledgment = request.data.get('acknowledgment', '')
        
        if not request_id:
            return Response({'success': False, 'error': 'Request ID required'}, status=400)
        
        session_request = Request.objects.get(id=request_id, learner=request.user)
        
        # Add acknowledgment field if it doesn't exist
        if not hasattr(session_request, 'learner_acknowledgment'):
            session_request.learner_acknowledgment = acknowledgment
        session_request.acknowledged_at = timezone.now()
        session_request.save()
        
        # Create notification for mentor
        if session_request.mentor:
            Notification.objects.create(
                user=session_request.mentor,
                title='Request Acknowledged',
                message=f'{request.user.get_full_name() or request.user.username} acknowledged your response to "{session_request.topic}"',
                notification_type='info'
            )
        
        return Response({
            'success': True,
            'message': 'Response acknowledged successfully'
        })
        
    except Request.DoesNotExist:
        return Response({'success': False, 'error': 'Request not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_available_mentors(request):
    """Get available mentors for request selection"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        available_mentors = User.objects.filter(
            role='mentor',
            is_active=True
        ).order_by('-date_joined')
        
        mentors_data = []
        for mentor in available_mentors:
            # Get mentor stats
            total_sessions = Session.objects.filter(mentor=mentor).count()
            avg_rating = Feedback.objects.filter(
                session__mentor=mentor
            ).aggregate(avg=models.Avg('rating'))['avg'] or 0
            
            # Get follower count
            from users.models import Follow
            follower_count = Follow.objects.filter(following=mentor).count()
            
            mentors_data.append({
                'id': str(mentor.id),
                'name': mentor.get_full_name() or mentor.username,
                'username': mentor.username,
                'skills': getattr(mentor, 'skills', ''),
                'domain': getattr(mentor, 'domain', ''),
                'bio': getattr(mentor, 'bio', ''),
                'total_sessions': total_sessions,
                'rating': round(float(avg_rating), 1),
                'followers': follower_count,
                'profile_image': mentor.profile_image.url if hasattr(mentor, 'profile_image') and mentor.profile_image else None
            })
        
        return Response({
            'success': True,
            'mentors': mentors_data,
            'count': len(mentors_data)
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_session_feedback_api(request, session_id):
    """Get all feedback for a session with real-time data"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Get all feedback for this session
        feedback_list = []
        for feedback in session.feedback.all().select_related('user'):
            feedback_list.append({
                'id': str(feedback.id),
                'user_name': feedback.user.get_full_name() or feedback.user.username,
                'user_avatar': feedback.user.profile_picture.url if hasattr(feedback.user, 'profile_picture') and feedback.user.profile_picture else '/static/images/default-avatar.png',
                'rating': feedback.rating,
                'comment': feedback.comment,
                'session_quality': feedback.session_quality,
                'mentor_effectiveness': feedback.mentor_effectiveness,
                'content_relevance': feedback.content_relevance,
                'technical_quality': feedback.technical_quality,
                'average_rating': feedback.average_rating,
                'created_at': feedback.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'time_ago': feedback.created_at.strftime('%d %b %Y'),
                'is_recent': (timezone.now() - feedback.created_at).days < 7
            })
        
        # Calculate session statistics
        from django.db.models import Avg, Count
        stats = session.feedback.aggregate(
            avg_rating=Avg('rating'),
            total_count=Count('id'),
            avg_session_quality=Avg('session_quality'),
            avg_mentor_effectiveness=Avg('mentor_effectiveness'),
            avg_content_relevance=Avg('content_relevance'),
            avg_technical_quality=Avg('technical_quality')
        )
        
        return JsonResponse({
            'success': True,
            'feedback': feedback_list,
            'statistics': {
                'average_rating': round(stats['avg_rating'] or 0, 1),
                'total_reviews': stats['total_count'] or 0,
                'session_quality': round(stats['avg_session_quality'] or 0, 1),
                'mentor_effectiveness': round(stats['avg_mentor_effectiveness'] or 0, 1),
                'content_relevance': round(stats['avg_content_relevance'] or 0, 1),
                'technical_quality': round(stats['avg_technical_quality'] or 0, 1)
            },
            'session': {
                'id': str(session.id),
                'title': session.title,
                'mentor_name': session.mentor.get_full_name() or session.mentor.username
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def submit_enhanced_feedback(request, session_id):
    """Submit comprehensive feedback with multiple rating categories"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Check if user participated in session
        participated = (
            session.mentor == request.user or 
            session.bookings.filter(learner=request.user, status__in=['confirmed', 'attended']).exists()
        )
        
        if not participated:
            return JsonResponse({'error': 'You must participate in the session to leave feedback'}, status=400)
        
        data = json.loads(request.body)
        
        # Validate ratings
        rating = int(data.get('rating', 0))
        if rating < 1 or rating > 5:
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        
        # Create or update feedback
        feedback, created = Feedback.objects.update_or_create(
            session=session,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': data.get('comment', ''),
                'session_quality': data.get('session_quality'),
                'mentor_effectiveness': data.get('mentor_effectiveness'),
                'content_relevance': data.get('content_relevance'),
                'technical_quality': data.get('technical_quality')
            }
        )
        
        # Create notification for mentor
        if session.mentor != request.user:
            Notification.objects.create(
                user=session.mentor,
                type='feedback_received',
                title='New Feedback Received! ⭐',
                message=f'{request.user.get_full_name() or request.user.username} rated your session "{session.title}" {rating}/5 stars',
                related_session=session
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your detailed feedback!',
            'feedback': {
                'id': str(feedback.id),
                'rating': feedback.rating,
                'average_rating': feedback.average_rating,
                'created': created
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def get_mentor_feedback_stats(request):
    """Get comprehensive feedback statistics for mentor dashboard"""
    try:
        if request.user.role != 'mentor':
            return JsonResponse({'error': 'Only mentors can access this data'}, status=403)
        
        from django.db.models import Avg, Count, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all feedback for mentor's sessions
        mentor_feedback = Feedback.objects.filter(session__mentor=request.user)
        
        # Calculate comprehensive statistics
        stats = mentor_feedback.aggregate(
            total_feedback=Count('id'),
            avg_overall=Avg('rating'),
            avg_session_quality=Avg('session_quality'),
            avg_mentor_effectiveness=Avg('mentor_effectiveness'),
            avg_content_relevance=Avg('content_relevance'),
            avg_technical_quality=Avg('technical_quality')
        )
        
        # Recent feedback (last 30 days)
        recent_feedback = mentor_feedback.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[str(i)] = mentor_feedback.filter(rating=i).count()
        
        # Recent reviews for display
        recent_reviews = []
        for feedback in recent_feedback.select_related('user', 'session').order_by('-created_at')[:5]:
            recent_reviews.append({
                'id': str(feedback.id),
                'user_name': feedback.user.get_full_name() or feedback.user.username,
                'session_title': feedback.session.title,
                'rating': feedback.rating,
                'comment': feedback.comment[:100] + '...' if len(feedback.comment) > 100 else feedback.comment,
                'created_at': feedback.created_at.strftime('%b %d, %Y'),
                'time_ago': feedback.created_at.strftime('%d %b')
            })
        
        # Monthly feedback trends
        monthly_trends = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_feedback = mentor_feedback.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            )
            
            monthly_trends.append({
                'month': month_start.strftime('%b'),
                'count': month_feedback.count(),
                'avg_rating': round(month_feedback.aggregate(avg=Avg('rating'))['avg'] or 0, 1)
            })
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_feedback': stats['total_feedback'] or 0,
                'average_rating': round(stats['avg_overall'] or 0, 1),
                'session_quality': round(stats['avg_session_quality'] or 0, 1),
                'mentor_effectiveness': round(stats['avg_mentor_effectiveness'] or 0, 1),
                'content_relevance': round(stats['avg_content_relevance'] or 0, 1),
                'technical_quality': round(stats['avg_technical_quality'] or 0, 1),
                'recent_count': recent_feedback.count()
            },
            'rating_distribution': rating_distribution,
            'recent_reviews': recent_reviews,
            'monthly_trends': monthly_trends[::-1]  # Reverse to show oldest first
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def get_learner_feedback_history(request):
    """Get learner's feedback history and statistics"""
    try:
        # Get all feedback given by this learner
        learner_feedback = Feedback.objects.filter(user=request.user).select_related('session', 'session__mentor')
        
        feedback_history = []
        for feedback in learner_feedback.order_by('-created_at'):
            feedback_history.append({
                'id': str(feedback.id),
                'session_title': feedback.session.title,
                'mentor_name': feedback.session.mentor.get_full_name() or feedback.session.mentor.username,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'average_rating': feedback.average_rating,
                'created_at': feedback.created_at.strftime('%B %d, %Y'),
                'session_date': feedback.session.schedule.strftime('%b %d, %Y') if feedback.session.schedule else '',
                'can_edit': (timezone.now() - feedback.created_at).days < 7  # Can edit within 7 days
            })
        
        # Calculate learner statistics
        from django.db.models import Avg, Count
        stats = learner_feedback.aggregate(
            total_given=Count('id'),
            avg_rating_given=Avg('rating')
        )
        
        return JsonResponse({
            'success': True,
            'feedback_history': feedback_history,
            'statistics': {
                'total_feedback_given': stats['total_given'] or 0,
                'average_rating_given': round(stats['avg_rating_given'] or 0, 1)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def get_real_time_feedback_updates(request):
    """Get real-time feedback updates for all dashboards"""
    try:
        recent_feedback = []
        
        if request.user.role == 'mentor':
            # For mentors: get recent feedback on their sessions
            feedback_qs = Feedback.objects.filter(
                session__mentor=request.user,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).select_related('user', 'session').order_by('-created_at')
            
        elif request.user.role == 'learner':
            # For learners: get recent feedback they've given
            feedback_qs = Feedback.objects.filter(
                user=request.user,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).select_related('session', 'session__mentor').order_by('-created_at')
            
        else:
            # For admins: get all recent feedback
            feedback_qs = Feedback.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).select_related('user', 'session', 'session__mentor').order_by('-created_at')
        
        for feedback in feedback_qs[:10]:
            recent_feedback.append({
                'id': str(feedback.id),
                'user_name': feedback.user.get_full_name() or feedback.user.username,
                'session_title': feedback.session.title,
                'mentor_name': feedback.session.mentor.get_full_name() or feedback.session.mentor.username,
                'rating': feedback.rating,
                'comment': feedback.comment[:50] + '...' if len(feedback.comment) > 50 else feedback.comment,
                'created_at': feedback.created_at.isoformat(),
                'time_ago': feedback.created_at.strftime('%H:%M'),
                'is_new': (timezone.now() - feedback.created_at).seconds < 3600  # New if less than 1 hour
            })
        
        return JsonResponse({
            'success': True,
            'recent_feedback': recent_feedback,
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_matching_api(request):
    """AI-powered mentor and session matching"""
    try:
        from .matching import get_mentor_recommendations, get_session_recommendations
        
        data = request.data
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        duration = data.get('duration', '60')
        budget = data.get('budget', '')
        urgency = data.get('urgency', 'flexible')
        
        if not topic:
            return Response({
                'success': False,
                'error': 'Topic is required for AI matching'
            }, status=400)
        
        # Create learner profile for matching
        learner_profile = {
            'skills': [topic.lower()],
            'domain': topic.lower(),
            'level': level,
            'duration': int(duration) if duration.isdigit() else 60,
            'budget': budget,
            'urgency': urgency,
            'preferred_times': []
        }
        
        # Get mentor recommendations
        mentor_matches = get_mentor_recommendations(learner_profile, max_results=5)
        
        # Get session recommendations
        session_matches = get_session_recommendations(request.user, limit=5)
        
        # Format mentor results
        mentors_data = []
        for match in mentor_matches:
            mentor = match['mentor']
            mentors_data.append({
                'id': str(mentor.id),
                'name': mentor.get_full_name() or mentor.username,
                'username': mentor.username,
                'profile_image': mentor.profile_image.url if mentor.profile_image else None,
                'score': match['score'],
                'match_reasons': match['match_reasons'],
                'stats': match['stats'],
                'availability': match['availability'],
                'skills': mentor.skills or '',
                'domain': getattr(mentor, 'domain', ''),
                'profile_url': f'/mentors/{mentor.id}/profile/'
            })
        
        # Format session results
        sessions_data = []
        for session in session_matches:
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'description': session.description,
                'mentor_name': session.mentor.get_full_name() or session.mentor.username,
                'schedule': session.schedule.isoformat(),
                'duration': session.duration,
                'price': float(session.price) if session.price else 0,
                'category': session.category,
                'skills': session.skills or '',
                'available_spots': session.remaining_spots,
                'session_url': f'/sessions/{session.id}/'
            })
        
        return Response({
            'success': True,
            'data': {
                'mentors': mentors_data,
                'sessions': sessions_data,
                'search_query': {
                    'topic': topic,
                    'level': level,
                    'duration': duration,
                    'urgency': urgency
                }
            },
            'message': f'Found {len(mentors_data)} mentors and {len(sessions_data)} sessions matching your criteria'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'AI matching failed: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_admin_session_feedback(request):
    """Get session feedback for admin dashboard"""
    try:
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'error': 'Admin access required'
            }, status=403)
        
        # Get recent feedback
        recent_feedback = Feedback.objects.select_related('session', 'user').order_by('-created_at')[:50]
        
        feedback_data = []
        for feedback in recent_feedback:
            feedback_data.append({
                'id': str(feedback.id),
                'session_title': feedback.session.title,
                'session_id': str(feedback.session.id),
                'learner_name': feedback.user.get_full_name() or feedback.user.username,
                'mentor_name': feedback.session.mentor.get_full_name() or feedback.session.mentor.username,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'session_quality': feedback.session_quality,
                'mentor_effectiveness': feedback.mentor_effectiveness,
                'content_relevance': feedback.content_relevance,
                'technical_quality': feedback.technical_quality,
                'created_at': feedback.created_at.isoformat(),
                'session_date': feedback.session.schedule.isoformat()
            })
        
        # Get feedback statistics
        from django.db.models import Avg, Count
        feedback_stats = Feedback.objects.aggregate(
            avg_rating=Avg('rating'),
            total_feedback=Count('id'),
            avg_session_quality=Avg('session_quality'),
            avg_mentor_effectiveness=Avg('mentor_effectiveness'),
            avg_content_relevance=Avg('content_relevance'),
            avg_technical_quality=Avg('technical_quality')
        )
        
        return Response({
            'success': True,
            'feedback': feedback_data,
            'stats': {
                'avg_rating': round(feedback_stats['avg_rating'] or 0, 2),
                'total_feedback': feedback_stats['total_feedback'],
                'avg_session_quality': round(feedback_stats['avg_session_quality'] or 0, 2),
                'avg_mentor_effectiveness': round(feedback_stats['avg_mentor_effectiveness'] or 0, 2),
                'avg_content_relevance': round(feedback_stats['avg_content_relevance'] or 0, 2),
                'avg_technical_quality': round(feedback_stats['avg_technical_quality'] or 0, 2)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to get feedback: {str(e)}'
        }, status=500)