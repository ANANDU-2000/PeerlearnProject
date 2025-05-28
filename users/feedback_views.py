"""
Views for handling user app feedback system
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json
from datetime import timedelta

# Import the feedback models
from .app_feedback import AppFeedback, FeedbackNotification

def app_feedback_page(request):
    """Display the feedback form page"""
    return render(request, 'feedback/app_feedback.html')

@require_http_methods(["POST"])
def submit_feedback(request):
    """Handle feedback submission via AJAX"""
    try:
        # Get form data
        rating = int(request.POST.get('rating', 0))
        category = request.POST.get('category', 'general')
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Validate required fields
        if not rating or rating < 1 or rating > 5:
            return JsonResponse({
                'success': False,
                'message': 'Please select a valid rating (1-5 stars).'
            })
        
        if not title or not message:
            return JsonResponse({
                'success': False,
                'message': 'Please fill in both title and message fields.'
            })
        
        # Handle user information
        if request.user.is_authenticated:
            user = request.user
            user_email = user.email or email
        else:
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Please provide your email address.'
                })
            
            # For anonymous users, try to find existing user or create placeholder
            user = None
            user_email = email
        
        # Get user's IP and user agent
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create feedback record
        feedback = AppFeedback.objects.create(
            user=user,
            email=user_email,
            rating=rating,
            category=category,
            title=title,
            message=message,
            ip_address=ip_address,
            user_agent=user_agent,
            status='pending'
        )
        
        # Create notification for admin
        FeedbackNotification.objects.create(
            feedback=feedback,
            notification_type='new_feedback',
            message=f'New {rating}-star feedback received from {user.username if user else user_email}',
            is_read=False
        )
        
        # Send notification email to admin (if configured)
        try:
            send_admin_notification_email(feedback)
        except Exception as e:
            print(f"Failed to send admin notification email: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your feedback! We appreciate your input.',
            'feedback_id': feedback.id
        })
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while submitting your feedback. Please try again.'
        })

def get_client_ip(request):
    """Get the client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def send_admin_notification_email(feedback):
    """Send email notification to admin about new feedback"""
    try:
        subject = f'New {feedback.rating}★ Feedback - {feedback.title}'
        message = f"""
New feedback received on PeerLearn:

Rating: {feedback.rating_stars} ({feedback.rating}/5)
Category: {feedback.get_category_display()}
User: {feedback.user.username if feedback.user else 'Anonymous'}
Email: {feedback.email}
Title: {feedback.title}

Message:
{feedback.message}

Review and respond at: {settings.SITE_URL}/admin-dashboard/dashboard/

Submitted: {feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')}
IP: {feedback.ip_address}
        """
        
        # Send to admin email (you can configure this in settings)
        admin_emails = ['admin@peerlearn.com']  # Configure this
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send admin notification: {e}")

@login_required
def admin_feedback_api(request):
    """API endpoint for admin to get feedback data"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        # Get all feedback with statistics
        all_feedback = AppFeedback.objects.select_related('user', 'admin_user').order_by('-created_at')
        
        feedback_list = []
        for feedback in all_feedback[:50]:  # Limit to recent 50
            feedback_list.append({
                'id': feedback.id,
                'user_name': feedback.user.username if feedback.user else 'Anonymous',
                'email': feedback.email,
                'rating': feedback.rating,
                'rating_stars': feedback.rating_stars,
                'category': feedback.get_category_display(),
                'title': feedback.title,
                'message': feedback.message,
                'status': feedback.get_status_display(),
                'admin_reply': feedback.admin_reply,
                'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'time_ago': feedback.time_since_created,
                'is_new': feedback.is_new,
            })
        
        # Calculate statistics
        total_feedback = AppFeedback.objects.count()
        pending_replies = AppFeedback.objects.filter(status='pending').count()
        avg_rating = AppFeedback.get_average_rating()
        weekly_feedback = AppFeedback.get_weekly_feedback().count()
        
        return JsonResponse({
            'success': True,
            'feedback': feedback_list,
            'statistics': {
                'total_feedback': total_feedback,
                'pending_replies': pending_replies,
                'average_rating': avg_rating,
                'weekly_feedback': weekly_feedback,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["POST"])
def admin_reply_feedback(request):
    """Handle admin replies to feedback"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        feedback_id = data.get('feedback_id')
        reply_message = data.get('reply_message', '').strip()
        send_email = data.get('send_email', True)
        
        if not feedback_id or not reply_message:
            return JsonResponse({
                'success': False,
                'message': 'Missing feedback ID or reply message.'
            })
        
        # Get feedback
        feedback = AppFeedback.objects.get(id=feedback_id)
        
        # Update feedback with admin reply
        feedback.admin_reply = reply_message
        feedback.admin_user = request.user
        feedback.status = 'replied'
        feedback.replied_at = timezone.now()
        feedback.reply_sent_via_email = send_email
        feedback.save()
        
        # Create notification
        FeedbackNotification.objects.create(
            feedback=feedback,
            notification_type='admin_reply',
            message=f'Admin replied to feedback: {feedback.title[:50]}',
            is_read=False
        )
        
        # Send email to user if requested
        if send_email:
            try:
                send_feedback_reply_email(feedback)
            except Exception as e:
                print(f"Failed to send reply email: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Reply sent successfully!'
        })
        
    except AppFeedback.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Feedback not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def send_feedback_reply_email(feedback):
    """Send email reply to user"""
    try:
        subject = f'Reply to your PeerLearn feedback: {feedback.title}'
        message = f"""
Hello {feedback.user.username if feedback.user else 'there'},

Thank you for your feedback about PeerLearn. We've reviewed your comments and wanted to respond:

Your Feedback ({feedback.rating}★):
"{feedback.message}"

Our Response:
{feedback.admin_reply}

We truly appreciate you taking the time to share your thoughts. Your feedback helps us improve PeerLearn for everyone.

If you have any additional questions or concerns, please don't hesitate to reach out.

Best regards,
The PeerLearn Team

---
This is an automated response to your feedback submitted on {feedback.created_at.strftime('%Y-%m-%d')}.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [feedback.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send reply email: {e}")

@login_required
def admin_notifications_api(request):
    """API endpoint for getting admin notifications"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        # Get recent notifications
        notifications = FeedbackNotification.objects.filter(
            is_read=False
        ).order_by('-created_at')[:10]
        
        notification_list = []
        for notif in notifications:
            notification_list.append({
                'id': notif.id,
                'type': notif.notification_type,
                'title': notif.get_notification_type_display(),
                'message': notif.message,
                'time': notif.created_at.strftime('%H:%M'),
                'unread': not notif.is_read
            })
        
        unread_count = FeedbackNotification.objects.filter(is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'notifications': notification_list,
            'unread_count': unread_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })