"""
Advanced Razorpay Gift Payment System for PeerLearn
Real payment processing for gifts and donations during WebRTC sessions
"""
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from sessions.models import Session, Booking
from users.models import Notification
import json
import os


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
        Notification.objects.create(
            user=session.mentor,
            title='Gift Payment Initiated!',
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
        Notification.objects.create(
            user=session.mentor,
            title='Gift Received! 🎁',
            message=f'You received ₹{amount} from {from_username}! Message: {message}',
            type='gift_received'
        )
        
        # Create confirmation notification for sender
        from django.contrib.auth.models import User
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


@login_required
def gift_payment_page(request):
    """Render gift payment page"""
    return render(request, 'payments/gift_payment.html', {
        'razorpay_key': os.getenv('RAZORPAY_KEY_ID')
    })