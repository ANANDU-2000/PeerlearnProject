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
from .models import Session, Booking, Feedback, RoomToken, SessionParticipant, Notification
from .forms import SessionForm, FeedbackForm
import razorpay
import os
from django.db.models import Avg, Count

@login_required
def session_list(request):
    """List all available sessions for booking"""
    sessions = Session.objects.filter(
        status='scheduled',
        schedule__gt=timezone.now()
    ).select_related('mentor').prefetch_related('bookings')
    
    # Add availability info
    for session in sessions:
        session.available_spots = session.remaining_spots
        session.is_booked = session.bookings.filter(learner=request.user, status='confirmed').exists()
    
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
    
    # Session status and actions
    can_book = (request.user.is_learner and 
                not session.is_full and 
                session.status == 'scheduled' and
                not user_booking)
    
    can_join = (user_booking and 
                session.is_live and 
                user_booking.can_join)
    
    context = {
        'session': session,
        'user_booking': user_booking,
        'feedback_list': feedback_list,
        'mentor_stats': mentor_stats,
        'can_book': can_book,
        'can_join': can_join,
        'available_spots': session.remaining_spots,
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
@require_http_methods(["GET", "POST"])
def book_session(request, session_id):
    """Book a session for a learner - handle both free and paid sessions"""
    print(f"DEBUG: Book session called - User: {request.user.username}, Role: {getattr(request.user, 'role', 'No role')}, Session: {session_id}")
    
    # Check user role more flexibly
    if not getattr(request.user, 'is_learner', True) and getattr(request.user, 'role', None) != 'learner':
        messages.error(request, 'Only learners can book sessions.')
        print(f"DEBUG: User role check failed - redirecting to session detail")
        return redirect('session_detail', session_id=session_id)
    
    session = get_object_or_404(Session, id=session_id)
    print(f"DEBUG: Session found - Title: {session.title}, Status: {session.status}, Price: {session.price}")
    
    # Validate booking
    if session.is_full:
        messages.error(request, 'Session is full.')
        print(f"DEBUG: Session is full - redirecting")
        return redirect('session_detail', session_id=session_id)
    
    if session.status != 'scheduled':
        messages.error(request, f'Session is not available for booking. Current status: {session.status}')
        print(f"DEBUG: Session status check failed - Status: {session.status}")
        return redirect('session_detail', session_id=session_id)
    
    # Check if already booked
    existing_booking = Booking.objects.filter(
        learner=request.user,
        session=session
    ).first()
    
    if existing_booking:
        messages.info(request, 'You are already booked for this session.')
        print(f"DEBUG: Already booked - redirecting")
        return redirect('session_detail', session_id=session_id)
    
    # For both free and paid sessions, redirect to checkout page
    print(f"DEBUG: All validations passed - redirecting to payment page")
    return redirect('razorpay_checkout', session_id=session_id)

@login_required
def razorpay_checkout(request, session_id):
    """Handle both free and paid session booking"""
    session = get_object_or_404(Session, id=session_id)
    print(f"DEBUG: Checkout page accessed - Session: {session.title}, Price: {session.price}, Method: {request.method}")
    
    # Check if user already booked
    existing_booking = Booking.objects.filter(
        learner=request.user,
        session=session
    ).first()
    
    if existing_booking:
        messages.info(request, 'You are already booked for this session.')
        return redirect('my_sessions')
    
    # Handle form submission (both free and paid)
    if request.method == 'POST':
        print(f"DEBUG: Processing booking - User: {request.user.username}, Session: {session.title}")
        
        # Create booking regardless of price
        booking = Booking.objects.create(
            learner=request.user,
            session=session,
            status='confirmed',
            payment_status='completed' if session.price and session.price > 0 else 'pending'
        )
        
        if session.price and session.price > 0:
            messages.success(request, f'🎉 Successfully enrolled in "{session.title}" for ₹{session.price}! (Demo payment completed)')
        else:
            messages.success(request, f'🎉 Successfully enrolled in free session "{session.title}"!')
        
        print(f"DEBUG: Booking created successfully - ID: {booking.id}")
        return redirect('my_sessions')
    
    # Display checkout page
    context = {
        'session': session,
        'user': request.user,
        'is_free': not session.price or session.price <= 0,
        'razorpay_key_id': 'rzp_test_JTeqXMBguhg25H',  # Updated with actual key
        'amount': session.price if session.price else 0,
    }
    
    print(f"DEBUG: Displaying checkout page - Free: {context['is_free']}")
    return render(request, 'payments/razorpay_checkout.html', context)

@login_required
def create_session(request):
    """Create a new session"""
    if request.user.role != 'mentor':
        messages.error(request, 'Only mentors can create sessions.')
        return redirect('learner_dashboard')
    
    if request.method == 'POST':
        form = SessionForm(request.POST, request.FILES)
        if form.is_valid():
            session = form.save(commit=False)
            session.mentor = request.user
            session.save()
            messages.success(request, 'Session created successfully!')
            return redirect('mentor_dashboard')
    else:
        form = SessionForm()
    
    return render(request, 'sessions/create_advanced.html', {'form': form})

@login_required
def publish_session(request, session_id):
    """Publish a draft session to make it available for booking"""
    session = get_object_or_404(Session, id=session_id, mentor=request.user)
    
    if session.status != 'draft':
        messages.error(request, 'Only draft sessions can be published.')
        return redirect('mentor_dashboard')
    
    session.status = 'scheduled'
    session.save()
    messages.success(request, f'Session "{session.title}" has been published and is now available for booking!')
    return redirect('mentor_dashboard')

@login_required
def unpublish_session(request, session_id):
    """Unpublish a scheduled session back to draft"""
    session = get_object_or_404(Session, id=session_id, mentor=request.user)
    
    if session.status != 'scheduled':
        messages.error(request, 'Only scheduled sessions can be unpublished.')
        return redirect('mentor_dashboard')
    
    # Check if anyone has booked this session
    if session.bookings.filter(status='confirmed').exists():
        messages.error(request, 'Cannot unpublish session that has confirmed bookings.')
        return redirect('mentor_dashboard')
    
    session.status = 'draft'
    session.save()
    messages.success(request, f'Session "{session.title}" has been unpublished and is now in draft mode.')
    return redirect('mentor_dashboard')

@login_required
def edit_session(request, session_id):
    """Edit an existing session"""
    session = get_object_or_404(Session, id=session_id, mentor=request.user)
    
    if request.method == 'POST':
        form = SessionForm(request.POST, request.FILES, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session updated successfully!')
            return redirect('mentor_dashboard')
    else:
        form = SessionForm(instance=session)
    
    return render(request, 'sessions/create_advanced.html', {'form': form, 'session': session})

@login_required
def session_room(request, session_id):
    """Join the live session room"""
    session = get_object_or_404(Session, id=session_id)
    
    print(f"DEBUG: Session room access - User: {request.user.id}, Session: {session_id}")
    print(f"DEBUG: Session status: {session.status}, Mentor: {session.mentor.id}")
    
    # Verify user has access
    if request.user == session.mentor:
        user_role = 'mentor'
        booking = None
        print(f"DEBUG: User is mentor for session {session_id}")
    else:
        user_role = 'learner'
        booking = Booking.objects.filter(
            session=session, 
            learner=request.user, 
            status__in=['confirmed', 'booked', 'attended']
        ).first()
        
        if not booking:
            print(f"DEBUG: No valid booking found for learner {request.user.id} in session {session_id}")
            messages.error(request, 'You do not have access to this session.')
            return redirect('session_detail', session_id=session_id)
        
        print(f"DEBUG: Found booking {booking.id} with status {booking.status}")
        
        # Check if can join
        if not booking.can_join:
            print(f"DEBUG: Booking {booking.id} cannot join yet")
            messages.error(request, 'You cannot join this session yet.')
            return redirect('session_detail', session_id=session_id)
    
    # Create or get room token
    token, created = RoomToken.objects.get_or_create(
        session=session,
        user=request.user,
        defaults={'expires_at': timezone.now() + timezone.timedelta(hours=2)}
    )
    
    print(f"DEBUG: Room token created/found: {token.token}")
    
    # Mark user as joined if learner
    if user_role == 'learner' and booking and not booking.joined_at:
        booking.mark_joined()
        print(f"DEBUG: Marked learner as joined")
    
    # Create session participant record
    participant, created = SessionParticipant.objects.get_or_create(
        session=session,
        user=request.user,
        defaults={'is_mentor': user_role == 'mentor'}
    )
    
    print(f"DEBUG: Session participant {'created' if created else 'found'}: {participant.id}")
    
    context = {
        'session': session,
        'user_role': user_role,
        'room_token': token.token,
        'is_waiting_room': session.status == 'scheduled',
        'participant': participant,
    }
    
    return render(request, 'sessions/webrtc_room.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request, session_id):
    """Start a session (mentor only)"""
    session = get_object_or_404(Session, id=session_id, mentor=request.user)
    
    try:
        session.start_session()
        return Response({
            'status': 'success',
            'message': 'Session started successfully',
            'session_id': str(session.id)
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, session_id):
    """End a session (mentor only)"""
    session = get_object_or_404(Session, id=session_id, mentor=request.user)
    
    try:
        session.end_session()
        return Response({
            'status': 'success',
            'message': 'Session ended successfully',
            'session_id': str(session.id)
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@login_required
def submit_feedback(request, session_id):
    """Submit feedback for a completed session"""
    session = get_object_or_404(Session, id=session_id)
    
    # Check if user participated in this session
    if request.user == session.mentor:
        booking = None
    else:
        booking = get_object_or_404(Booking, 
                                   session=session, 
                                   learner=request.user)
    
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
    
    context = {
        'session': session,
        'form': form,
        'booking': booking
    }
    
    return render(request, 'feedback/feedback.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_api_list(request):
    """API endpoint for session list"""
    sessions = Session.objects.filter(
        status='scheduled',
        schedule__gt=timezone.now()
    ).select_related('mentor')
    
    data = []
    for session in sessions:
        data.append({
            'id': str(session.id),
            'title': session.title,
            'description': session.description,
            'mentor': session.mentor.username,
            'schedule': session.schedule.isoformat(),
            'duration': session.duration,
            'price': float(session.price) if session.price else 0,
            'current_participants': session.current_participants,
            'max_participants': session.max_participants,
            'category': session.category,
        })
    
    return Response(data)

@login_required
def waiting_room(request, session_id):
    """Waiting room for session participants"""
    session = get_object_or_404(Session, id=session_id)
    
    # Verify access
    if request.user == session.mentor:
        user_role = 'mentor'
        booking = None
    else:
        user_role = 'learner'
        booking = get_object_or_404(Booking, 
                                   session=session, 
                                   learner=request.user, 
                                   status='confirmed')
    
    # Get other participants
    participants = []
    if user_role == 'mentor':
        participants = session.bookings.filter(status='confirmed').select_related('learner')
    else:
        # Learners can see other learners and mentor
        participants = session.bookings.filter(status='confirmed').select_related('learner')
        participants = list(participants) + [{'learner': session.mentor, 'is_mentor': True}]
    
    context = {
        'session': session,
        'user_role': user_role,
        'booking': booking,
        'participants': participants,
        'can_start': session.can_start and user_role == 'mentor',
    }
    
    return render(request, 'sessions/waiting_room.html', context)

@login_required
def join_waiting_room_api(request, session_id):
    """API to join waiting room"""
    session = get_object_or_404(Session, id=session_id)
    
    # Verify access
    if request.user == session.mentor:
        user_role = 'mentor'
    else:
        user_role = 'learner'
        get_object_or_404(Booking, 
                         session=session, 
                         learner=request.user, 
                         status='confirmed')
    
    # Create session participant record
    participant, created = SessionParticipant.objects.get_or_create(
        session=session,
        user=request.user,
        defaults={'is_mentor': user_role == 'mentor'}
    )
    
    return JsonResponse({
        'status': 'success',
        'user_role': user_role,
        'session_status': session.status,
        'can_start': session.can_start and user_role == 'mentor',
    })

@login_required
@require_http_methods(["POST"])
def leave_session(request, session_id):
    """Leave the session"""
    session = get_object_or_404(Session, id=session_id)
    
    # Update participant record
    participant = SessionParticipant.objects.filter(
        session=session,
        user=request.user
    ).first()
    
    if participant:
        participant.mark_left()
    
    # Update booking if learner
    if request.user != session.mentor:
        booking = Booking.objects.filter(
            session=session,
            learner=request.user
        ).first()
        if booking:
            booking.mark_left()
    
    return JsonResponse({'status': 'success'})

@login_required
def session_analytics(request, session_id):
    """View session analytics (mentor only)"""
    session = get_object_or_404(Session, id=session_id, mentor=request.user)
    
    # Get session statistics
    total_bookings = session.bookings.count()
    confirmed_bookings = session.bookings.filter(status='confirmed').count()
    attended_bookings = session.bookings.filter(status='attended').count()
    no_show_bookings = session.bookings.filter(status='no_show').count()
    
    # Calculate average attendance duration
    attendance_durations = session.bookings.filter(
        attendance_duration__isnull=False
    ).values_list('attendance_duration', flat=True)
    
    avg_attendance = sum(attendance_durations) / len(attendance_durations) if attendance_durations else 0
    
    # Get feedback statistics
    feedback_stats = session.feedback.aggregate(
        avg_rating=Avg('rating'),
        total_feedback=Count('id')
    )
    
    context = {
        'session': session,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'attended_bookings': attended_bookings,
        'no_show_bookings': no_show_bookings,
        'avg_attendance': round(avg_attendance, 1),
        'feedback_stats': feedback_stats,
    }
    
    return render(request, 'sessions/analytics.html', context)

@login_required
def notifications_list(request):
    """View user notifications"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:50]
    
    return render(request, 'notifications/list.html', {
        'notifications': notifications
    })

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return JsonResponse({'status': 'success'})

# Gift Payment System
@login_required
@require_http_methods(["POST"])
def create_gift_payment(request):
    """Create a gift payment for a session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        amount = data.get('amount')
        message = data.get('message', '')
        
        session = get_object_or_404(Session, id=session_id)
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET')))
        
        # Create payment order
        payment_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f'gift_{session_id}_{request.user.id}',
            'notes': {
                'session_id': str(session_id),
                'learner_id': str(request.user.id),
                'mentor_id': str(session.mentor.id),
                'message': message
            }
        }
        
        order = client.order.create(data=payment_data)
        
        return JsonResponse({
            'status': 'success',
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'key_id': os.getenv('RAZORPAY_KEY_ID')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def verify_gift_payment(request):
    """Verify gift payment after completion"""
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        order_id = data.get('order_id')
        signature = data.get('signature')
        
        # Verify payment signature
        client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET')))
        
        # Verify signature
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        
        client.utility.verify_payment_signature(params_dict)
        
        # Get payment details
        payment = client.payment.fetch(payment_id)
        
        # Update booking payment status
        session_id = payment['notes'].get('session_id')
        learner_id = payment['notes'].get('learner_id')
        
        if session_id and learner_id:
            booking = Booking.objects.filter(
                session_id=session_id,
                learner_id=learner_id
            ).first()
            
            if booking:
                booking.payment_status = 'completed'
                booking.payment_id = payment_id
                booking.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment verified successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def verify_payment(request, session_id):
    """Verify real Razorpay payment and create booking"""
    session = get_object_or_404(Session, id=session_id)
    
    try:
        # Get payment details from request
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        print(f"Payment verification - Payment ID: {payment_id}, Order ID: {order_id}")
        
        if not all([payment_id, order_id, signature]):
            messages.error(request, 'Invalid payment data received.')
            return redirect('payment_failure', session_id=session_id)
        
        # Use real Razorpay keys for verification
        razorpay_key_secret = '7FYtozDO4Tb6w0aEZwYtc6DB'
        client = razorpay.Client(auth=('rzp_test_JTeqXMBguhg25H', razorpay_key_secret))
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            print("Payment signature verified successfully!")
        except razorpay.errors.SignatureVerificationError as e:
            print(f"Payment verification failed: {e}")
            messages.error(request, 'Payment verification failed.')
            return redirect('payment_failure', session_id=session_id)
        
        # Check if booking already exists (prevent duplicate)
        existing_booking = Booking.objects.filter(
            learner=request.user,
            session=session
        ).first()
        
        if existing_booking:
            messages.info(request, 'You are already booked for this session.')
            return redirect('my_sessions')
        
        # Payment verified - create booking
        booking = Booking.objects.create(
            learner=request.user,
            session=session,
            status='confirmed',
            payment_status='completed',
            payment_id=payment_id
        )
        
        print(f"Booking created successfully: {booking.id}")
        messages.success(request, f'Payment successful! You are now booked for "{session.title}".')
        return redirect('my_sessions')
        
    except Exception as e:
        print(f"Payment processing error: {e}")
        messages.error(request, 'Payment processing failed. Please try again.')
        return redirect('payment_failure', session_id=session_id)

@login_required
def payment_success(request, session_id):
    """Display payment success page"""
    session = get_object_or_404(Session, id=session_id)
    booking = get_object_or_404(Booking, session=session, learner=request.user)
    
    context = {
        'session': session,
        'booking': booking,
        'success_message': f'Successfully booked "{session.title}" with {session.mentor.get_full_name}!'
    }
    
    return render(request, 'payments/success.html', context)

@login_required  
def payment_failure(request, session_id):
    """Display payment failure page"""
    session = get_object_or_404(Session, id=session_id)
    
    context = {
        'session': session,
        'error_message': 'Payment failed. Please try booking again.'
    }
    
    return render(request, 'payments/failure.html', context)

@login_required
def my_sessions(request):
    """Show learner's session history with sub-tabs"""
    if not request.user.is_learner:
        messages.error(request, 'Only learners can access this page.')
        return redirect('learner_dashboard')
    
    # Get all bookings for the learner (including all statuses)
    bookings = Booking.objects.filter(
        learner=request.user
    ).select_related('session', 'session__mentor').order_by('-session__schedule')
    
    # Debug: Print all booking statuses
    for booking in bookings:
        print(f"DEBUG: Booking for session '{booking.session.title}' - Status: {booking.status}, Session Status: {booking.session.status}")
    
    # Also get sessions where learner is the mentor (for testing)
    mentor_sessions = Session.objects.filter(
        mentor=request.user
    ).order_by('-schedule')
    
    print(f"DEBUG: Found {len(bookings)} bookings for learner {request.user.username}")
    print(f"DEBUG: Found {len(mentor_sessions)} sessions where user is mentor")
    
    # If no bookings found, show a message
    if not bookings:
        context = {
            'upcoming_sessions': [],
            'completed_sessions': [],
            'live_sessions': [],
            'cancelled_sessions': [],
            'total_sessions': 0,
            'active_tab': 'upcoming',
            'no_bookings': True
        }
        return render(request, 'sessions/my_sessions.html', context)
    
    print(f"DEBUG: Found {len(bookings)} bookings for learner {request.user.username}")
    
    # Categorize sessions
    upcoming_sessions = []
    completed_sessions = []
    live_sessions = []
    cancelled_sessions = []
    
    for booking in bookings:
        session = booking.session
        print(f"DEBUG: Processing session '{session.title}' - Status: {session.status}, Schedule: {session.schedule}, Now: {timezone.now()}")
        
        # Check if session is in the future (upcoming)
        if session.schedule > timezone.now() and session.status in ['scheduled', 'draft']:
            upcoming_sessions.append(booking)
            print(f"DEBUG: Added to upcoming: {session.title}")
        # Check if session is currently live
        elif session.status == 'live':
            live_sessions.append(booking)
            print(f"DEBUG: Added to live: {session.title}")
        # Check if session is completed
        elif session.status == 'completed':
            completed_sessions.append(booking)
            print(f"DEBUG: Added to completed: {session.title}")
        # Check if session is cancelled
        elif session.status == 'cancelled':
            cancelled_sessions.append(booking)
            print(f"DEBUG: Added to cancelled: {session.title}")
        # If session is in the past but not completed, treat as completed
        elif session.schedule <= timezone.now() and session.status not in ['cancelled', 'live']:
            completed_sessions.append(booking)
            print(f"DEBUG: Added to completed (past): {session.title}")
    
    print(f"DEBUG: Final counts - Upcoming: {len(upcoming_sessions)}, Live: {len(live_sessions)}, Completed: {len(completed_sessions)}, Cancelled: {len(cancelled_sessions)}")
    
    context = {
        'upcoming_sessions': upcoming_sessions,
        'completed_sessions': completed_sessions,
        'live_sessions': live_sessions,
        'cancelled_sessions': cancelled_sessions,
        'total_sessions': len(bookings),
        'active_tab': request.GET.get('tab', 'upcoming')  # Default to upcoming tab
    }
    
    return render(request, 'sessions/my_sessions.html', context)
