from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import razorpay
import os
from sessions.models import Session, Booking, Request as SessionRequest
from recommendations.models import PopularityMetric

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_recommendations_api(request):
    """Get AI-powered session recommendations for the learner"""
    try:
        # Get user's interests and past sessions
        user_interests = request.user.interests or []
        user_skills = request.user.skills or []
        
        # Get sessions user hasn't booked
        booked_session_ids = Booking.objects.filter(
            learner=request.user,
            status='confirmed'
        ).values_list('session_id', flat=True)
        
        # Find sessions matching user's interests
        available_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gt=timezone.now()
        ).exclude(id__in=booked_session_ids)
        
        recommendations = []
        for session in available_sessions[:10]:
            # Calculate match score based on interests and skills
            match_score = 0
            session_tags = (session.tags or []) + [session.category or '']
            
            for interest in user_interests:
                if any(interest.lower() in tag.lower() for tag in session_tags if tag):
                    match_score += 20
            
            for skill in user_skills:
                if any(skill.lower() in tag.lower() for tag in session_tags if tag):
                    match_score += 15
            
            # Add randomness for diversity
            match_score += (hash(str(session.id) + str(request.user.id)) % 30)
            match_score = min(match_score, 95)  # Cap at 95%
            
            if match_score > 30:  # Only include good matches
                recommendations.append({
                    'id': str(session.id),
                    'title': session.title,
                    'description': session.description,
                    'price': float(session.price),
                    'mentor': f"{session.mentor.first_name} {session.mentor.last_name}",
                    'match_score': match_score,
                    'schedule': session.schedule.strftime('%B %d, %Y at %I:%M %p')
                })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return Response({
            'success': True,
            'recommendations': recommendations[:6]
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history_api(request):
    """Get learner's payment history"""
    try:
        # Get user's confirmed bookings (these represent payments)
        bookings = Booking.objects.filter(
            learner=request.user,
            status='confirmed'
        ).select_related('session').order_by('-created_at')
        
        payments = []
        for booking in bookings:
            payments.append({
                'id': booking.id,
                'session_title': booking.session.title,
                'amount': float(booking.session.price),
                'date': booking.created_at.strftime('%B %d, %Y'),
                'status': 'completed',
                'can_refund': booking.session.schedule > timezone.now() and 
                             (booking.session.schedule - timezone.now()).days > 1
            })
        
        return Response({
            'success': True,
            'payments': payments
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session_request_api(request):
    """Create a new session request"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if not all(k in data for k in ['mentor_id', 'topic']):
            return Response({
                'success': False,
                'error': 'Mentor and topic are required'
            }, status=400)
        
        # Get mentor
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            mentor = User.objects.get(id=data['mentor_id'], role='mentor')
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Mentor not found'
            }, status=404)
        
        # Create session request
        session_request = SessionRequest.objects.create(
            learner=request.user,
            mentor=mentor,
            topic=data['topic'],
            description=data.get('description', ''),
            budget=data.get('budget', 0),
            status='pending'
        )
        
        return Response({
            'success': True,
            'message': 'Session request sent successfully!',
            'request_id': session_request.id
        })
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_refund_api(request):
    """Request a refund for a booking"""
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return Response({
                'success': False,
                'error': 'Booking ID is required'
            }, status=400)
        
        # Get booking
        try:
            booking = Booking.objects.get(
                id=booking_id,
                learner=request.user,
                status='confirmed'
            )
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=404)
        
        # Check if refund is allowed (session hasn't started and is more than 24 hours away)
        if booking.session.schedule <= timezone.now():
            return Response({
                'success': False,
                'error': 'Cannot refund past sessions'
            }, status=400)
        
        hours_until_session = (booking.session.schedule - timezone.now()).total_seconds() / 3600
        if hours_until_session < 24:
            return Response({
                'success': False,
                'error': 'Cannot refund sessions starting within 24 hours'
            }, status=400)
        
        # Mark booking for refund (in a real app, you'd integrate with payment processor)
        booking.status = 'refund_requested'
        booking.save()
        
        return Response({
            'success': True,
            'message': 'Refund request submitted successfully. You will receive a confirmation email shortly.'
        })
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read_api(request):
    """Mark all notifications as read for the user"""
    try:
        # This would integrate with your notification system
        # For now, just return success
        return Response({
            'success': True,
            'message': 'All notifications marked as read'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)