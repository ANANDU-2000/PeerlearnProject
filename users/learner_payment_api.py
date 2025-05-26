"""
Advanced Learner Payment API with Razorpay Integration
Real payment processing, booking management, earnings tracking, and mentor reviews
"""
import razorpay
import json
import os
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from sessions.models import Session, Booking, Feedback
# from users.models import Notification  # Will be created later


# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(
    os.getenv('RAZORPAY_KEY_ID'),
    os.getenv('RAZORPAY_KEY_SECRET')
))


@login_required
@require_http_methods(["GET"])
def get_learner_payment_history(request):
    """Get complete payment history for learner dashboard"""
    try:
        user = request.user
        
        # Get all bookings with payment information
        bookings = Booking.objects.filter(
            learner=user
        ).select_related('session', 'session__mentor').order_by('-created_at')
        
        payment_history = []
        total_spent = 0
        
        for booking in bookings:
            session = booking.session
            amount = session.price if session.price else 0
            total_spent += amount
            
            payment_history.append({
                'id': booking.id,
                'session_title': session.title,
                'mentor_name': session.mentor.get_full_name() or session.mentor.username,
                'amount': amount,
                'currency': 'INR',
                'status': booking.status,
                'booking_date': booking.created_at.strftime('%Y-%m-%d %H:%M'),
                'session_date': session.schedule.strftime('%Y-%m-%d %H:%M') if session.schedule else None,
                'session_duration': session.duration,
                'payment_method': 'Razorpay',
                'can_review': booking.status == 'completed'
            })
        
        # Get gift payment history
        # Note: This would require a separate GiftPayment model in production
        
        return JsonResponse({
            'success': True,
            'payment_history': payment_history,
            'total_spent': total_spent,
            'total_sessions': len(payment_history),
            'currency': 'INR'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_session_payment(request):
    """Create Razorpay payment for session booking"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        # Get session details
        session = Session.objects.get(id=session_id)
        
        if session.price <= 0:
            return JsonResponse({'error': 'This is a free session'}, status=400)
        
        # Check if already booked
        existing_booking = Booking.objects.filter(
            session=session,
            learner=request.user
        ).first()
        
        if existing_booking:
            return JsonResponse({'error': 'You have already booked this session'}, status=400)
        
        # Create Razorpay order
        order_data = {
            'amount': int(session.price * 100),  # Convert to paise
            'currency': 'INR',
            'notes': {
                'session_id': str(session_id),
                'learner_id': str(request.user.id),
                'mentor_id': str(session.mentor.id),
                'session_title': session.title,
                'type': 'session_booking'
            }
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        return JsonResponse({
            'success': True,
            'order_id': razorpay_order['id'],
            'amount': session.price,
            'currency': 'INR',
            'key': os.getenv('RAZORPAY_KEY_ID'),
            'name': 'PeerLearn Session',
            'description': f'Booking for {session.title}',
            'session_details': {
                'title': session.title,
                'mentor': session.mentor.get_full_name() or session.mentor.username,
                'duration': session.duration,
                'schedule': session.schedule.strftime('%Y-%m-%d %H:%M') if session.schedule else None
            },
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


@csrf_exempt
@require_http_methods(["POST"])
def verify_session_payment(request):
    """Verify and process session booking payment"""
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
        
        # Get payment and order details
        payment = razorpay_client.payment.fetch(payment_id)
        order = razorpay_client.order.fetch(order_id)
        
        # Extract data from order notes
        notes = order.get('notes', {})
        session_id = notes.get('session_id')
        learner_id = notes.get('learner_id')
        
        # Get session and create booking
        session = Session.objects.get(id=session_id)
        learner = User.objects.get(id=learner_id)
        
        # Create confirmed booking
        booking = Booking.objects.create(
            session=session,
            learner=learner,
            status='confirmed',
            payment_id=payment_id,
            amount_paid=payment.get('amount', 0) // 100
        )
        
        # Update session participant count
        session.current_participants = session.current_participants + 1
        session.save()
        
        # Create notifications (will be implemented with notification system)
        # Notification.objects.create(user=session.mentor, title='New Session Booking! 💰', message=f'{learner.username} has booked your session "{session.title}" for ₹{session.price}', type='session_booked')
        # Notification.objects.create(user=learner, title='Session Booked Successfully!', message=f'You have successfully booked "{session.title}" with {session.mentor.username}', type='booking_confirmed')
        
        return JsonResponse({
            'success': True,
            'message': 'Session booked successfully!',
            'booking_id': booking.id,
            'session_title': session.title,
            'amount': session.price,
            'payment_id': payment_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_learner_analytics(request):
    """Get comprehensive learner analytics and spending insights"""
    try:
        user = request.user
        
        # Get booking statistics
        total_bookings = Booking.objects.filter(learner=user).count()
        completed_sessions = Booking.objects.filter(learner=user, status='completed').count()
        upcoming_sessions = Booking.objects.filter(
            learner=user, 
            status='confirmed',
            session__schedule__gt=timezone.now()
        ).count()
        
        # Calculate spending analytics
        total_spent = Booking.objects.filter(
            learner=user,
            status__in=['confirmed', 'completed']
        ).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        # Monthly spending trend
        monthly_spending = []
        for i in range(6):
            start_date = timezone.now() - timedelta(days=30*(i+1))
            end_date = timezone.now() - timedelta(days=30*i)
            
            month_spent = Booking.objects.filter(
                learner=user,
                created_at__range=[start_date, end_date],
                status__in=['confirmed', 'completed']
            ).aggregate(total=Sum('amount_paid'))['total'] or 0
            
            monthly_spending.append({
                'month': start_date.strftime('%b %Y'),
                'amount': month_spent
            })
        
        # Get feedback given
        reviews_given = Feedback.objects.filter(user=user).count()
        average_rating_given = Feedback.objects.filter(user=user).aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'total_bookings': total_bookings,
                'completed_sessions': completed_sessions,
                'upcoming_sessions': upcoming_sessions,
                'total_spent': total_spent,
                'currency': 'INR',
                'reviews_given': reviews_given,
                'average_rating_given': round(average_rating_given, 1),
                'monthly_spending': monthly_spending[::-1]  # Reverse for chronological order
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def submit_mentor_review(request):
    """Submit review and rating for a mentor after session completion"""
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or rating < 1 or rating > 5:
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        
        # Get booking and verify it belongs to user and is completed
        booking = Booking.objects.get(
            id=booking_id,
            learner=request.user,
            status='completed'
        )
        
        # Check if review already exists
        existing_feedback = Feedback.objects.filter(
            session=booking.session,
            user=request.user
        ).first()
        
        if existing_feedback:
            return JsonResponse({'error': 'You have already reviewed this session'}, status=400)
        
        # Create feedback
        feedback = Feedback.objects.create(
            session=booking.session,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        # Create notification for mentor
        Notification.objects.create(
            user=booking.session.mentor,
            title='New Review Received! ⭐',
            message=f'{request.user.username} rated your session "{booking.session.title}" {rating}/5 stars',
            type='review_received'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!',
            'feedback_id': feedback.id
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found or not completed'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_mentor_reviews(request):
    """Get all reviews and ratings given by the learner"""
    try:
        user = request.user
        
        reviews = Feedback.objects.filter(user=user).select_related(
            'session', 'session__mentor'
        ).order_by('-created_at')
        
        review_list = []
        for review in reviews:
            review_list.append({
                'id': review.id,
                'session_title': review.session.title,
                'mentor_name': review.session.mentor.get_full_name() or review.session.mentor.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M'),
                'session_date': review.session.schedule.strftime('%Y-%m-%d') if review.session.schedule else None
            })
        
        return JsonResponse({
            'success': True,
            'reviews': review_list,
            'total_reviews': len(review_list)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)