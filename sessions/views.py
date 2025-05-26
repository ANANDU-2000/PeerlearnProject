from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
from .models import Session, Booking, Feedback, RoomToken
from .forms import SessionForm, FeedbackForm

@login_required
def session_list(request):
    """List all available sessions for booking"""
    sessions = Session.objects.filter(
        status='scheduled',
        schedule__gt=timezone.now()
    ).select_related('mentor')
    
    return render(request, 'sessions/list.html', {'sessions': sessions})

@login_required
def session_detail(request, session_id):
    """View session details and allow booking"""
    session = get_object_or_404(Session, id=session_id)
    user_booking = None
    
    # Check if user has booked this session
    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(
            learner=request.user,
            session=session,
            status='confirmed'
        ).first()
    
    # Get session feedback/reviews
    feedback_list = session.feedback.select_related('user').order_by('-created_at')
    
    # Calculate mentor stats
    mentor_stats = {
        'sessions_count': Session.objects.filter(mentor=session.mentor, status='completed').count(),
        'avg_rating': 4.8,  # Calculate from actual feedback
        'total_students': 156  # Calculate from bookings
    }
    
    context = {
        'session': session,
        'user_booking': user_booking,
        'feedback_list': feedback_list,
        'mentor_stats': mentor_stats,
    }
    
    return render(request, 'sessions/detail_advanced.html', context)
    
    if request.user.is_learner:
        try:
            user_booking = Booking.objects.get(learner=request.user, session=session)
        except Booking.DoesNotExist:
            pass
    
    context = {
        'session': session,
        'user_booking': user_booking,
        'can_book': (request.user.is_learner and 
                    not session.is_full and 
                    session.status == 'scheduled' and
                    not user_booking)
    }
    
    return render(request, 'sessions/detail.html', context)

@login_required
@require_http_methods(["POST"])
def book_session(request, session_id):
    """Book a session for a learner"""
    if not request.user.is_learner:
        messages.error(request, 'Only learners can book sessions.')
        return redirect('session_detail', session_id=session_id)
    
    session = get_object_or_404(Session, id=session_id)
    
    if session.is_full:
        messages.error(request, 'Session is full.')
        return redirect('learner_dashboard')
    
    booking, created = Booking.objects.get_or_create(
        learner=request.user,
        session=session,
        defaults={'status': 'confirmed'}
    )
    
    if created:
        messages.success(request, f'Successfully booked "{session.title}"! Check your My Sessions tab.')
    else:
        messages.info(request, 'You are already booked for this session.')
    
    return redirect('learner_dashboard')

@login_required
def create_session(request):
    """Redirect to mentor dashboard with create modal"""
    if request.user.role != 'mentor':
        messages.error(request, 'Only mentors can create sessions.')
        return redirect('learner_dashboard')
    
    # Redirect to mentor dashboard where the create modal exists
    messages.info(request, 'Click the "Create Session" button to create a new session.')
    return redirect('mentor_dashboard')

@login_required
def session_room(request, session_id):
    """WebRTC room for live sessions"""
    session = get_object_or_404(Session, id=session_id)
    
    # Check if user has access to this room
    has_access = False
    if request.user == session.mentor:
        has_access = True
    elif request.user.is_learner:
        try:
            booking = Booking.objects.get(learner=request.user, session=session, status='confirmed')
            has_access = True
        except Booking.DoesNotExist:
            pass
    
    if not has_access:
        messages.error(request, 'You do not have access to this session.')
        return redirect('session_detail', session_id=session_id)
    
    # Create or get room token
    room_token, created = RoomToken.objects.get_or_create(
        session=session,
        user=request.user,
        defaults={
            'expires_at': timezone.now() + timezone.timedelta(hours=2)
        }
    )
    
    context = {
        'session': session,
        'room_token': room_token.token,
        'is_mentor': request.user == session.mentor,
    }
    
    return render(request, 'session_room.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request, session_id):
    """Start a session (mentor only)"""
    session = get_object_or_404(Session, id=session_id)
    
    if request.user != session.mentor:
        return Response({'error': 'Only the mentor can start the session'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    if not session.can_start:
        return Response({'error': 'Session cannot be started yet'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    session.status = 'live'
    session.save()
    
    return Response({'status': 'Session started successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, session_id):
    """End a session (mentor only)"""
    session = get_object_or_404(Session, id=session_id)
    
    if request.user != session.mentor:
        return Response({'error': 'Only the mentor can end the session'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    session.status = 'completed'
    session.save()
    
    return Response({'status': 'Session ended successfully'})

@login_required
def submit_feedback(request, session_id):
    """Submit feedback for a completed session"""
    session = get_object_or_404(Session, id=session_id)
    
    if session.status != 'completed':
        messages.error(request, 'Can only provide feedback for completed sessions.')
        return redirect('session_detail', session_id=session_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.session = session
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('session_detail', session_id=session_id)
    else:
        form = FeedbackForm()
    
    return render(request, 'sessions/feedback.html', {'form': form, 'session': session})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_api_list(request):
    """API endpoint for session list"""
    if request.user.is_mentor:
        sessions = Session.objects.filter(mentor=request.user)
    else:
        sessions = Session.objects.filter(status='scheduled', schedule__gt=timezone.now())
    
    data = []
    for session in sessions:
        data.append({
            'id': str(session.id),
            'title': session.title,
            'description': session.description,
            'schedule': session.schedule.isoformat(),
            'duration': session.duration,
            'status': session.status,
            'current_participants': session.current_participants,
            'max_participants': session.max_participants,
            'mentor': session.mentor.username,
            'can_start': session.can_start if request.user == session.mentor else False,
        })
    
    return Response(data)
