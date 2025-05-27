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
import razorpay
import os

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
    
    # Calculate real mentor stats from database
    from django.db.models import Avg, Count
    mentor_sessions = Session.objects.filter(mentor=session.mentor, status='completed')
    total_students = Booking.objects.filter(
        session__mentor=session.mentor,
        status='confirmed'
    ).values('learner').distinct().count()
    
    avg_rating = session.feedback.aggregate(avg=Avg('rating'))['avg'] or 0.0
    
    mentor_stats = {
        'sessions_count': mentor_sessions.count(),
        'avg_rating': round(avg_rating, 1),
        'total_students': total_students
    }
    
    context = {
        'session': session,
        'user_booking': user_booking,
        'feedback_list': feedback_list,
        'mentor_stats': mentor_stats,
    }
    
    return render(request, 'sessions/detail_advanced.html', context)

def session_detail_new(request, session_id):
    """New Coursera-style session detail view"""
    session = get_object_or_404(Session, id=session_id)
    user_booking = None
    
    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(
            session=session, 
            learner=request.user
        ).first()
    
    context = {
        'session': session,
        'user_booking': user_booking,
    }
    
    return render(request, 'sessions/session_view_new.html', context)
    
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
    """Book a session for a learner - handle both free and paid sessions"""
    if not request.user.is_learner:
        messages.error(request, 'Only learners can book sessions.')
        return redirect('session_detail', session_id=session_id)
    
    session = get_object_or_404(Session, id=session_id)
    
    if session.is_full:
        messages.error(request, 'Session is full.')
        return redirect('learner_dashboard')
    
    # Check if already booked
    existing_booking = Booking.objects.filter(
        learner=request.user,
        session=session
    ).first()
    
    if existing_booking:
        messages.info(request, 'You are already booked for this session.')
        return redirect('learner_dashboard')
    
    # Check if this is a paid session
    if session.price and session.price > 0:
        # Redirect to payment page for paid sessions
        messages.info(request, f'This session costs ₹{session.price}. Please complete payment to confirm your booking.')
        return redirect('razorpay_checkout', session_id=session_id)
    else:
        # Free session - book directly
        booking = Booking.objects.create(
            learner=request.user,
            session=session,
            status='confirmed'
        )
        messages.success(request, f'Successfully booked "{session.title}"! Check your My Sessions tab.')
        return redirect('learner_dashboard')

@login_required
def razorpay_checkout(request, session_id):
    """Display Razorpay payment page for session booking"""
    session = get_object_or_404(Session, id=session_id)
    
    # Check if user already booked
    existing_booking = Booking.objects.filter(
        learner=request.user,
        session=session
    ).first()
    
    if existing_booking:
        messages.info(request, 'You are already booked for this session.')
        return redirect('learner_dashboard')
    
    # Check if session is free
    if not session.price or session.price <= 0:
        messages.info(request, 'This is a free session. Booking directly...')
        Booking.objects.create(
            learner=request.user,
            session=session,
            status='confirmed'
        )
        return redirect('learner_dashboard')
    
    context = {
        'session': session,
        'razorpay_key_id': os.getenv('RAZORPAY_KEY_ID'),
        'user': request.user
    }
    
    return render(request, 'payments/razorpay_checkout.html', context)

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
def edit_session(request, session_id):
    """Edit an existing session"""
    session = get_object_or_404(Session, id=session_id, mentor=request.user)
    
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session updated successfully!')
            return redirect('mentor_dashboard')
    else:
        form = SessionForm(instance=session)
    
    return render(request, 'sessions/edit_session.html', {
        'form': form,
        'session': session
    })

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
    
    # Simple room access without token dependency
    room_token = {
        'token': str(session.id),
        'expires_at': timezone.now() + timezone.timedelta(hours=2)
    }
    
    context = {
        'session': session,
        'room_token': room_token['token'],
        'is_mentor': request.user == session.mentor,
    }
    
    return render(request, 'sessions/webrtc_room.html', context)

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

@login_required
def create_session(request):
    """Advanced session creation with full functionality"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can create sessions.')
        return redirect('learner_dashboard')
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        schedule = request.POST.get('schedule')
        duration = request.POST.get('duration', 60)
        max_participants = request.POST.get('max_participants', 10)
        status = request.POST.get('status', 'draft')
        
        try:
            # Create session with all fields including thumbnail
            session = Session.objects.create(
                mentor=request.user,
                title=title,
                description=description,
                thumbnail=request.FILES.get('thumbnail'),
                category=request.POST.get('category', 'programming'),
                skills=request.POST.get('skills', ''),
                price=request.POST.get('price') if request.POST.get('pricing') == 'paid' else None,
                schedule=schedule,
                duration=int(duration),
                max_participants=int(max_participants),
                status=status
            )
            
            if status == 'scheduled':
                messages.success(request, f'Session "{title}" created and published successfully! Learners can now book it.')
            else:
                messages.success(request, f'Session "{title}" saved as draft successfully! You can publish it later.')
            
            return redirect('mentor_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating session: {str(e)}')
    
    return render(request, 'sessions/create_advanced.html')

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


@login_required
def waiting_room(request, session_id):
    """WebRTC waiting room for early access"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Check if user has permission to join
        can_join = False
        if request.user == session.mentor:
            can_join = True
        elif Booking.objects.filter(session=session, learner=request.user, status='confirmed').exists():
            can_join = True
        
        if not can_join:
            messages.error(request, 'You are not authorized to join this session.')
            return redirect('session_detail', session_id=session_id)
        
        context = {
            'session': session,
            'user_role': 'mentor' if request.user == session.mentor else 'learner',
            'room_id': str(session_id),
            'is_waiting_room': True
        }
        
        return render(request, 'sessions/webrtc_room.html', context)
        
    except Exception as e:
        messages.error(request, f'Error accessing waiting room: {str(e)}')
        return redirect('session_list')


@login_required
def session_room(request, session_id):
    """Advanced WebRTC room for live video sessions"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Check if user has permission to join
        can_join = False
        user_role = 'learner'
        
        if request.user == session.mentor:
            can_join = True
            user_role = 'mentor'
        elif Booking.objects.filter(session=session, learner=request.user, status='confirmed').exists():
            can_join = True
            user_role = 'learner'
        
        if not can_join:
            messages.error(request, 'You are not authorized to join this session.')
            return redirect('session_detail', session_id=session_id)
        
        # Get all participants for this session
        bookings = Booking.objects.filter(session=session, status='confirmed')
        participants = []
        
        # Add mentor
        participants.append({
            'id': session.mentor.id,
            'name': session.mentor.get_full_name() or session.mentor.username,
            'role': 'mentor',
            'is_ready': getattr(session, 'mentor_ready', False)
        })
        
        # Add learners
        for booking in bookings:
            participants.append({
                'id': booking.learner.id,
                'name': booking.learner.get_full_name() or booking.learner.username,
                'role': 'learner',
                'is_ready': getattr(booking, 'learner_ready', False)
            })
        
        context = {
            'session': session,
            'user_role': user_role,
            'room_id': str(session_id),
            'participants': participants,
            'is_waiting_room': False,
            'can_start': user_role == 'mentor',
            'session_title': session.title,
            'session_duration': session.duration
        }
        
        return render(request, 'sessions/webrtc_room.html', context)
        
    except Exception as e:
        messages.error(request, f'Error accessing session room: {str(e)}')
        return redirect('session_list')


# Initialize Razorpay client with your credentials
razorpay_client = razorpay.Client(auth=(
    os.getenv('RAZORPAY_KEY_ID'),
    os.getenv('RAZORPAY_KEY_SECRET')
))


@login_required
@require_http_methods(["POST"])
def create_gift_payment(request):
    """Create Razorpay payment for gifts/donations"""
    try:
        data = json.loads(request.body)
        amount = int(data.get('amount', 0))
        message = data.get('message', '')
        session_id = data.get('session_id')
        
        if amount < 1:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Validate session exists
        session = Session.objects.get(id=session_id)
        
        # Check if user is enrolled in session (booked/paid)
        booking = Booking.objects.filter(
            session=session, 
            learner=request.user, 
            status__in=['confirmed', 'completed']
        ).first()
        
        if not booking:
            return JsonResponse({
                'error': 'You must be enrolled in this session to send gifts'
            }, status=403)
        
        # Create Razorpay order
        order_data = {
            'amount': amount * 100,  # Amount in paise
            'currency': 'INR',
            'notes': {
                'session_id': str(session_id),
                'from_user': request.user.username,
                'to_mentor': session.mentor.username,
                'message': message,
                'type': 'gift_payment'
            }
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        # Create notification for mentor
        from users.models import Notification
        Notification.objects.create(
            user=session.mentor,
            title='Gift Payment Initiated! 🎁',
            message=f'{request.user.username} is sending you a gift of ₹{amount}! Message: {message}',
            type='gift_pending'
        )
        
        return JsonResponse({
            'success': True,
            'order_id': razorpay_order['id'],
            'amount': amount,
            'currency': 'INR',
            'key': os.getenv('RAZORPAY_KEY_ID'),
            'name': 'PeerLearn Gift',
            'description': f'Gift for {session.mentor.username}',
            'prefill': {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            },
            'theme': {
                'color': '#0056d3'
            }
        })
        
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def start_session(request, session_id):
    """Start a session - FIXED FOR MENTORS"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Check if user is the mentor
        if request.user != session.mentor:
            return JsonResponse({'error': 'Only the mentor can start this session'}, status=403)
        
        # Update session status
        session.status = 'in_progress'
        session.save()
        
        # Create notification for all booked learners
        from users.models import Notification
        booked_learners = Booking.objects.filter(
            session=session, 
            status='confirmed'
        ).values_list('learner', flat=True)
        
        for learner_id in booked_learners:
            Notification.objects.create(
                user_id=learner_id,
                title='🟢 Session Started!',
                message=f'"{session.title}" has started. Join now!',
                type='session_started'
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Session started successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def end_session(request, session_id):
    """End a session"""
    try:
        session = get_object_or_404(Session, id=session_id)
        
        # Check if user is the mentor
        if request.user != session.mentor:
            return JsonResponse({'error': 'Only the mentor can end this session'}, status=403)
        
        # Update session status
        session.status = 'completed'
        session.save()
        
        # Update all bookings to completed
        Booking.objects.filter(session=session, status='confirmed').update(status='completed')
        
        return JsonResponse({
            'success': True,
            'message': 'Session ended successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_gift_payment(request):
    """Verify and process completed gift payment"""
    try:
        data = json.loads(request.body)
        
        # Verify payment with Razorpay
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
        except:
            return JsonResponse({'error': 'Invalid payment signature'}, status=400)
        
        # Get payment details
        payment = razorpay_client.payment.fetch(payment_id)
        order = razorpay_client.order.fetch(order_id)
        
        # Extract data from order notes
        notes = order.get('notes', {})
        session_id = notes.get('session_id')
        from_username = notes.get('from_user')
        to_username = notes.get('to_mentor')
        message = notes.get('message', '')
        amount = payment.get('amount', 0) // 100  # Convert from paise
        
        # Get session and users
        session = Session.objects.get(id=session_id)
        
        # Create success notification for mentor
        from users.models import Notification
        from django.contrib.auth.models import User
        
        Notification.objects.create(
            user=session.mentor,
            title='Gift Received! 🎁',
            message=f'You received ₹{amount} from {from_username}! Message: {message}',
            type='gift_received'
        )
        
        # Create confirmation notification for sender
        sender = User.objects.get(username=from_username)
        Notification.objects.create(
            user=sender,
            title='Gift Sent Successfully!',
            message=f'Your gift of ₹{amount} has been sent to {to_username}',
            type='gift_sent'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Gift payment successful!',
            'amount': amount,
            'payment_id': payment_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
