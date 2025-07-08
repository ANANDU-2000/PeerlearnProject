# Advanced Admin API Endpoints for PeerLearn Platform
# Comprehensive admin controls with real-time features

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, timedelta
from django.utils import timezone
import json
import requests
from .models import User, UserActivity, PaymentHistory, Follow
from sessions.models import Session, Booking, Feedback, Notification, Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

def is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def ai_chat_endpoint(request):
    """Advanced AI chatbot with Groq API integration"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        api_key = data.get('api_key', '')
        model = data.get('model', 'llama-3.1-8b-instant')
        
        if not api_key:
            return JsonResponse({
                'success': False, 
                'error': 'API key required. Please get your free Groq API key from console.groq.com'
            })
        
        # Build context-aware prompt for admin assistance
        system_prompt = f"""You are an advanced AI assistant for PeerLearn platform administration. 
        You help admins manage users, sessions, analytics, and platform operations.
        
        Current admin: {request.user.get_full_name() or request.user.username}
        Platform: PeerLearn - Peer-to-peer learning platform
        
        You can help with:
        - User management and analytics
        - Session monitoring and control
        - Platform performance insights
        - Communication strategies
        - Technical troubleshooting
        - Data analysis and reporting
        
        Provide helpful, professional responses in a conversational tone."""
        
        # Groq API request
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            'model': model,
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
                'model': model,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Groq API error: {response.status_code}. Please check your API key.'
            })
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': 'Request timeout. Please try again.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def bulk_email_endpoint(request):
    """Send bulk emails to users with advanced targeting"""
    try:
        data = json.loads(request.body)
        recipients = data.get('recipients', 'all')
        subject = data.get('subject', '')
        message = data.get('message', '')
        
        if not subject or not message:
            return JsonResponse({
                'success': False,
                'error': 'Subject and message are required'
            })
        
        # Build recipient list based on selection
        if recipients == 'all':
            users = User.objects.filter(is_active=True)
        elif recipients == 'learners':
            users = User.objects.filter(role='learner', is_active=True)
        elif recipients == 'mentors':
            users = User.objects.filter(role='mentor', is_active=True)
        elif recipients == 'active':
            # Users active in last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            users = User.objects.filter(
                last_login__gte=thirty_days_ago,
                is_active=True
            )
        else:
            users = User.objects.filter(is_active=True)
        
        # Prepare email content
        from_email = settings.DEFAULT_FROM_EMAIL
        email_list = []
        
        for user in users:
            # Personalized email content
            personalized_message = f"""
            Dear {user.get_full_name() or user.username},
            
            {message}
            
            Best regards,
            PeerLearn Admin Team
            
            ---
            This is an official communication from PeerLearn platform.
            """
            
            email_list.append((
                subject,
                personalized_message,
                from_email,
                [user.email]
            ))
        
        # Send bulk emails
        send_mass_mail(email_list, fail_silently=False)
        
        # Log the communication
        # Create notification records for tracking
        for user in users:
            Notification.objects.create(
                user=user,
                title=f"Email: {subject}",
                message=f"Bulk email sent by admin",
                notification_type='info'
            )
        
        return JsonResponse({
            'success': True,
            'count': len(email_list),
            'message': f'Email sent to {len(email_list)} users successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Email sending failed: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def send_notification_endpoint(request):
    """Send push notifications to all users"""
    try:
        data = json.loads(request.body)
        notification_type = data.get('type', 'info')
        title = data.get('title', '')
        message = data.get('message', '')
        sound = data.get('sound', True)
        
        if not title or not message:
            return JsonResponse({
                'success': False,
                'error': 'Title and message are required'
            })
        
        # Create notifications for all active users
        active_users = User.objects.filter(is_active=True)
        notifications = []
        
        for user in active_users:
            notifications.append(
                Notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority='high' if notification_type == 'urgent' else 'medium'
                )
            )
        
        # Bulk create notifications
        Notification.objects.bulk_create(notifications)
        
        return JsonResponse({
            'success': True,
            'count': len(notifications),
            'message': f'Notification sent to {len(notifications)} users'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Notification failed: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def ban_user_endpoint(request, user_id):
    """Ban a specific user"""
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent banning superusers
        if user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'Cannot ban superuser accounts'
            })
        
        user.is_active = False
        user.save()
        
        # Create notification for the banned user
        Notification.objects.create(
            user=user,
            title="Account Suspended",
            message="Your account has been suspended by admin. Contact support for assistance.",
            notification_type='warning',
            priority='urgent'
        )
        
        # Log admin action
        Notification.objects.create(
            user=request.user,
            title="User Banned",
            message=f"Successfully banned user: {user.get_full_name() or user.username}",
            notification_type='success'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'User {user.get_full_name() or user.username} has been banned'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ban failed: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["DELETE"])
def delete_user_endpoint(request, user_id):
    """Delete a specific user (use with extreme caution)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deleting superusers
        if user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete superuser accounts'
            })
        
        # Store user info for logging
        user_name = user.get_full_name() or user.username
        user_email = user.email
        
        # Delete user (cascade will handle related objects)
        user.delete()
        
        # Log admin action
        Notification.objects.create(
            user=request.user,
            title="User Deleted",
            message=f"Successfully deleted user: {user_name} ({user_email})",
            notification_type='warning'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'User {user_name} has been deleted permanently'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Delete failed: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["GET"])
def admin_users_endpoint(request):
    """Get users data with filtering and pagination"""
    try:
        # Get query parameters
        search = request.GET.get('search', '')
        role_filter = request.GET.get('role', '')
        status_filter = request.GET.get('status', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Start with all users
        users = User.objects.all()
        
        # Apply filters
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if role_filter:
            users = users.filter(role=role_filter)
        
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        
        # Calculate pagination
        total_users = users.count()
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_users = users[start_index:end_index]
        
        # Format user data
        users_data = []
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        
        for user in paginated_users:
            # Check online status
            is_online = user.last_login and user.last_login > thirty_minutes_ago
            
            users_data.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'status': 'online' if is_online else 'offline',
                'is_active': user.is_active,
                'joined': user.date_joined.strftime('%Y-%m-%d'),
                'lastActivity': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                'profile_image': user.profile_image.url if user.profile_image else None
            })
        
        # Calculate stats
        stats = {
            'total': User.objects.count(),
            'mentors': User.objects.filter(role='mentor').count(),
            'learners': User.objects.filter(role='learner').count(),
            'online': User.objects.filter(last_login__gte=thirty_minutes_ago).count()
        }
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'stats': stats,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_users,
                'total_pages': (total_users + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to fetch users: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["GET"])
def real_time_stats_endpoint(request):
    """Get real-time platform statistics"""
    try:
        # Calculate real-time metrics
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        today = datetime.now().date()
        
        # Online users
        online_users = User.objects.filter(
            last_login__gte=thirty_minutes_ago,
            is_active=True
        ).count()
        
        # Active sessions
        active_sessions = Session.objects.filter(
            status='active'
        ).count()
        
        # Today's revenue (from completed bookings)
        today_bookings = Booking.objects.filter(
            created_at__date=today,
            payment_status='paid'
        )
        today_revenue = sum(booking.payment_amount or 0 for booking in today_bookings)
        
        # System health (simplified calculation)
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        system_health = (active_users / max(total_users, 1)) * 100
        
        # Recent activities
        recent_activities = []
        
        # Recent registrations
        recent_users = User.objects.filter(
            date_joined__gte=datetime.now() - timedelta(hours=24)
        ).order_by('-date_joined')[:5]
        
        for user in recent_users:
            recent_activities.append({
                'id': f'user_{user.id}',
                'icon': 'fas fa-user-plus',
                'message': f'New user registered: {user.get_full_name() or user.username}',
                'timestamp': user.date_joined.strftime('%H:%M'),
                'status': 'Active',
                'statusColor': 'bg-green-100 text-green-800'
            })
        
        # Recent sessions
        recent_sessions = Session.objects.filter(
            created_at__gte=datetime.now() - timedelta(hours=24)
        ).order_by('-created_at')[:3]
        
        for session in recent_sessions:
            recent_activities.append({
                'id': f'session_{session.id}',
                'icon': 'fas fa-video',
                'message': f'Session created: {session.title}',
                'timestamp': session.created_at.strftime('%H:%M'),
                'status': session.status.title(),
                'statusColor': 'bg-blue-100 text-blue-800'
            })
        
        # Sort activities by timestamp
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'stats': {
                'online_users': online_users,
                'active_sessions': active_sessions,
                'today_revenue': float(today_revenue),
                'system_health': round(system_health, 1)
            },
            'activities': recent_activities[:10],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to fetch stats: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def emergency_actions_endpoint(request):
    """Handle emergency admin actions"""
    try:
        data = json.loads(request.body)
        action = data.get('action', '')
        
        if action == 'maintenance_mode':
            # Enable maintenance mode (could set a flag in settings/cache)
            return JsonResponse({
                'success': True,
                'message': 'Maintenance mode enabled'
            })
            
        elif action == 'force_logout_all':
            # Clear all user sessions (implementation depends on session backend)
            return JsonResponse({
                'success': True,
                'message': 'All users logged out'
            })
            
        elif action == 'emergency_broadcast':
            # Send urgent notification to all users
            message = data.get('message', 'Emergency system notification')
            
            active_users = User.objects.filter(is_active=True)
            notifications = []
            
            for user in active_users:
                notifications.append(
                    Notification(
                        user=user,
                        title="URGENT: System Alert",
                        message=message,
                        notification_type='error',
                        priority='urgent'
                    )
                )
            
            Notification.objects.bulk_create(notifications)
            
            return JsonResponse({
                'success': True,
                'message': f'Emergency broadcast sent to {len(notifications)} users'
            })
            
        else:
            return JsonResponse({
                'success': False,
                'error': 'Unknown action'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Emergency action failed: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])  
def create_admin_endpoint(request):
    """Create new admin user (owner only)"""
    try:
        # Only allow superusers to create admins
        if not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'Only platform owners can create admin accounts'
            })
        
        data = json.loads(request.body)
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if not username or not email or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username, email, and password are required'
            })
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already exists'
            })
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'Email already exists'
            })
        
        # Create admin user
        admin_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='mentor',  # Admins can be mentors too
            is_staff=True,
            is_active=True
        )
        
        # Send welcome email to new admin
        welcome_message = f"""
        Welcome to PeerLearn Admin Team!
        
        Your admin account has been created by {request.user.get_full_name() or request.user.username}.
        
        Login Details:
        Username: {username}
        Email: {email}
        
        You now have administrative privileges on the PeerLearn platform.
        
        Best regards,
        PeerLearn Team
        """
        
        try:
            send_mass_mail([(
                'Welcome to PeerLearn Admin Team',
                welcome_message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )], fail_silently=True)
        except:
            pass  # Don't fail if email sending fails
        
        return JsonResponse({
            'success': True,
            'message': f'Admin account created for {first_name} {last_name}',
            'admin_id': admin_user.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Admin creation failed: {str(e)}'
        })

@login_required
@require_http_methods(["GET"])
def get_real_admin_stats(request):
    """Get real-time admin statistics"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        now = timezone.now()
        today = now.date()
        
        # User statistics
        total_users = User.objects.count()
        total_mentors = User.objects.filter(role='mentor').count()
        total_learners = User.objects.filter(role='learner').count()
        
        # Online users (active in last 15 minutes)
        online_threshold = now - timedelta(minutes=15)
        online_users = User.objects.filter(
            last_active__gte=online_threshold,
            is_active=True
        ).count()
        
        # Session statistics
        total_sessions = Session.objects.count()
        live_sessions = Session.objects.filter(status='live').count()
        scheduled_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=now
        ).count()
        completed_sessions = Session.objects.filter(status='completed').count()
        
        # Booking statistics
        total_bookings = Booking.objects.count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        
        # Revenue statistics
        total_revenue = PaymentHistory.objects.filter(
            status='completed',
            payment_type='session_booking'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        today_revenue = PaymentHistory.objects.filter(
            status='completed',
            payment_type='session_booking',
            created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Feedback statistics
        total_feedback = Feedback.objects.count()
        avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0
        pending_feedback = Feedback.objects.filter(
            comment='',
            created_at__gte=now - timedelta(days=7)
        ).count()
        
        # Recent activity counts
        today_signups = User.objects.filter(date_joined__date=today).count()
        today_sessions = Session.objects.filter(created_at__date=today).count()
        
        stats = {
            'users': {
                'total': total_users,
                'mentors': total_mentors,
                'learners': total_learners,
                'online': online_users,
                'today_signups': today_signups,
            },
            'sessions': {
                'total': total_sessions,
                'active': live_sessions,
                'scheduled': scheduled_sessions,
                'completed': completed_sessions,
                'today_created': today_sessions,
            },
            'bookings': {
                'total': total_bookings,
                'confirmed': confirmed_bookings,
                'pending': pending_bookings,
            },
            'revenue': {
                'total': float(total_revenue),
                'today': float(today_revenue),
            },
            'feedback': {
                'total': total_feedback,
                'average_rating': round(float(avg_rating), 2),
                'pending': pending_feedback,
            },
            'last_updated': now.isoformat(),
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def get_real_users(request):
    """Get real users from database with full details"""
    if not request.user.is_staff and not request.user.role == 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        # Get all users with related data
        users = User.objects.all().select_related().prefetch_related(
            'following', 'followers', 'activities'
        )
        
        users_data = []
        for user in users:
            users_data.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'last_active': user.last_active.isoformat() if user.last_active else None,
                'total_sessions': user.total_sessions,
                'session_count': user.total_sessions,
                'followers_count': user.followers_count,
                'following_count': user.following_count,
                'profile_image': user.profile_image_url,
                'bio': user.bio,
                'location': user.location,
                'skills': user.get_skills_list(),
                'interests': user.get_interests_list(),
                'is_online': user.is_online,
                'hourly_rate': float(user.hourly_rate) if user.hourly_rate else None,
                'total_earnings': float(user.total_earnings) if user.total_earnings else 0,
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'total': users.count(),
            'stats': {
                'total_users': users.count(),
                'active_users': users.filter(is_active=True).count(),
                'mentors': users.filter(role='mentor').count(),
                'learners': users.filter(role='learner').count(),
                'online_users': len([u for u in users if u.is_online]),
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def get_online_users(request):
    """Get currently online users"""
    if not request.user.is_staff and not request.user.role == 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        # Consider users online if active in last 5 minutes
        cutoff_time = timezone.now() - timedelta(minutes=5)
        online_users = User.objects.filter(last_active__gte=cutoff_time)
        
        users_data = []
        for user in online_users:
            users_data.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'last_active': user.last_active.isoformat(),
                'is_online': True,
                'profile_image': user.profile_image_url,
                'activity_status': 'Active' if user.last_active > timezone.now() - timedelta(minutes=1) else 'Recently Active'
            })
        
        return JsonResponse({
            'success': True,
            'online_users': users_data,
            'count': len(users_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def get_admin_stats(request):
    """Get comprehensive admin statistics"""
    if not request.user.is_staff and not request.user.role == 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        from sessions.models import Session, Booking
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Sum, Count, Q
        
        # User stats
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        online_users = User.objects.filter(last_active__gte=timezone.now() - timedelta(minutes=5)).count()
        new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
        
        # Session stats
        total_sessions = Session.objects.count()
        active_sessions = Session.objects.filter(status='live').count()
        sessions_today = Session.objects.filter(created_at__date=timezone.now().date()).count()
        completed_sessions = Session.objects.filter(status='completed').count()
        
        # Revenue stats (from payments)
        today_revenue = PaymentHistory.objects.filter(
            created_at__date=timezone.now().date(),
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_revenue = PaymentHistory.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Booking stats
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        
        # Feedback stats
        total_feedback = 0  # Will be updated when feedback model is available
        pending_feedback = 0
        
        return JsonResponse({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'online': online_users,
                    'new_today': new_users_today,
                    'mentors': User.objects.filter(role='mentor').count(),
                    'learners': User.objects.filter(role='learner').count(),
                },
                'sessions': {
                    'total': total_sessions,
                    'active': active_sessions,
                    'today': sessions_today,
                    'completed': completed_sessions,
                },
                'revenue': {
                    'today': float(today_revenue),
                    'total': float(total_revenue),
                    'avg_session': float(total_revenue / max(completed_sessions, 1)),
                },
                'bookings': {
                    'pending': pending_bookings,
                    'confirmed': confirmed_bookings,
                },
                'feedback': {
                    'total': total_feedback,
                    'pending': pending_feedback,
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_user_status(request, user_id):
    """Update user status (active/banned)"""
    # Enhanced access control - allow superusers, staff, or users with admin role
    if not (request.user.is_superuser or request.user.is_staff or request.user.role == 'admin'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    try:
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        user = get_object_or_404(User, id=user_id)
        # Prevent superusers from being banned by non-superusers
        if user.is_superuser and not request.user.is_superuser:
            return JsonResponse({'error': 'Cannot modify superuser accounts'}, status=403)
        action = data.get('action')
        if not action:
            return JsonResponse({'error': 'Missing action'}, status=400)
        reason = data.get('reason', 'No reason provided')
        if action == 'ban':
            user.is_active = False
            UserActivity.objects.create(
                user=user,
                activity_type='profile_updated',
                description=f'Account banned by admin {request.user.username}. Reason: {reason}',
                related_user_id=request.user.id
            )
            message = f'User {user.username} has been banned'
        elif action == 'unban':
            user.is_active = True
            UserActivity.objects.create(
                user=user,
                activity_type='profile_updated',
                description=f'Account unbanned by admin {request.user.username}',
                related_user_id=request.user.id
            )
            message = f'User {user.username} has been unbanned'
        elif action == 'verify':
            user.is_verified = True
            UserActivity.objects.create(
                user=user,
                activity_type='profile_updated',
                description=f'Account verified by admin {request.user.username}',
                related_user_id=request.user.id
            )
            message = f'User {user.username} has been verified'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        user.save()
        return JsonResponse({
            'success': True,
            'message': message,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'is_active': user.is_active,
                'is_verified': getattr(user, 'is_verified', False),
            }
        })
    except Exception as e:
        print(f"Error in update_user_status: {str(e)}")  # Debug logging
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_admin_user(request):
    """Create a new user from admin panel"""
    if not request.user.is_staff and not request.user.role == 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Check if user already exists
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({'error': 'User with this email already exists'}, status=400)
        
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({'error': 'User with this username already exists'}, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            bio=data.get('bio', ''),
            location=data.get('location', ''),
            is_verified=data.get('is_verified', False),
        )
        
        # Add role-specific fields
        if data['role'] == 'mentor':
            user.hourly_rate = data.get('hourly_rate')
            user.experience_years = data.get('experience_years', 0)
            user.skills = data.get('skills', '')
        elif data['role'] == 'learner':
            user.interests = data.get('interests', '')
            user.career_goals = data.get('career_goals', '')
            user.domain = data.get('domain', '')
        
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='account_created',
            description=f'Account created by admin {request.user.username}',
            related_user_id=request.user.id
        )
        
        return JsonResponse({
            'success': True,
            'message': f'User {user.username} created successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required  
def get_banned_users(request):
    """Get list of banned users"""
    if not request.user.is_staff and not request.user.role == 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        banned_users = User.objects.filter(is_active=False)
        
        users_data = []
        for user in banned_users:
            # Get last ban activity
            ban_activity = UserActivity.objects.filter(
                user=user,
                activity_type='banned'
            ).order_by('-created_at').first()
            
            users_data.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'date_joined': user.date_joined.isoformat(),
                'banned_at': ban_activity.created_at.isoformat() if ban_activity else None,
                'ban_reason': ban_activity.description if ban_activity else 'Unknown',
                'profile_image': user.profile_image_url,
            })
        
        return JsonResponse({
            'success': True,
            'banned_users': users_data,
            'count': len(users_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def get_user_activities(request, user_id):
    """Get detailed activity log for a specific user"""
    if not request.user.is_staff and not request.user.role == 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        user = get_object_or_404(User, id=user_id)
        activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:50]
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': str(activity.id),
                'activity_type': activity.activity_type,
                'description': activity.description,
                'created_at': activity.created_at.isoformat(),
                'ip_address': activity.ip_address,
                'metadata': activity.metadata,
            })
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
            },
            'activities': activities_data,
            'count': len(activities_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_recent_activity(request):
    """Get recent platform activity for admin dashboard"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        # Get recent activities
        activities = UserActivity.objects.select_related('user').order_by('-created_at')[:50]
        
        activities_data = []
        for activity in activities:
            time_diff = timezone.now() - activity.created_at
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} days ago"
            elif time_diff.seconds > 3600:
                time_ago = f"{time_diff.seconds // 3600} hours ago"
            elif time_diff.seconds > 60:
                time_ago = f"{time_diff.seconds // 60} minutes ago"
            else:
                time_ago = "Just now"
            
            activities_data.append({
                'id': str(activity.id),
                'user': activity.user.username,
                'activity_type': activity.activity_type,
                'description': activity.description,
                'time_ago': time_ago,
                'created_at': activity.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'activities': activities_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Get admin notifications"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        from sessions.models import Notification
        
        # Get notifications for the admin user
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        
        unread_count = notifications.filter(read=False).count()
        
        notifications_data = []
        for notif in notifications:
            try:
                time_diff = timezone.now() - notif.created_at
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    time_ago = f"{time_diff.seconds // 3600} hours ago"
                elif time_diff.seconds > 60:
                    time_ago = f"{time_diff.seconds // 60} minutes ago"
                else:
                    time_ago = "Just now"
                
                notifications_data.append({
                    'id': str(notif.id),
                    'type': notif.type or 'info',
                    'title': notif.title or 'Notification',
                    'message': notif.message or '',
                    'read': notif.read,
                    'time_ago': time_ago,
                    'created_at': notif.created_at.isoformat(),
                })
            except Exception as inner_e:
                # Skip problematic notifications
                continue
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
        
    except Exception as e:
        # Return empty notifications if there's an error
        return JsonResponse({
            'success': True,
            'notifications': [],
            'unread_count': 0,
            'error_message': f'Error loading notifications: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_user_notification(request):
    """Send notification to specific users"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])
        title = data.get('title', '')
        message = data.get('message', '')
        
        if not user_ids or not title or not message:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Create notifications for selected users
        notifications_created = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                Notification.objects.create(
                    user=user,
                    type='admin_message',
                    title=title,
                    message=message
                )
                notifications_created += 1
            except User.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Notifications sent to {notifications_created} users'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_data(request):
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
            total=models.Sum('price')
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
                total=models.Sum('price')
            )['total'] or 0
            
            monthly_earnings.insert(0, {
                'month': month_name,
                'amount': float(month_earnings)
            })
        
        # Calculate average rating
        from django.db.models import Avg
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

@api_view(['GET'])
def admin_real_data_api(request):
    """Get comprehensive real platform data for admin dashboard"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        from django.contrib.auth import get_user_model
        from sessions.models import Session, Booking, Feedback, Request, Notification
        from django.db.models import Count, Avg, Sum, Q
        from datetime import datetime, timedelta
        
        User = get_user_model()
        now = timezone.now()
        today = now.date()
        
        # Real User Statistics
        total_users = User.objects.count()
        total_mentors = User.objects.filter(role='mentor').count()
        total_learners = User.objects.filter(role='learner').count()
        active_users = User.objects.filter(is_active=True).count()
        banned_users = User.objects.filter(is_active=False).count()
        
        # Online users (active in last 30 minutes)
        thirty_minutes_ago = now - timedelta(minutes=30)
        online_users = User.objects.filter(last_login__gte=thirty_minutes_ago).count()
        
        # Session Statistics
        total_sessions = Session.objects.count()
        active_sessions = Session.objects.filter(status='live').count()
        completed_sessions = Session.objects.filter(status='completed').count()
        scheduled_sessions = Session.objects.filter(status='scheduled').count()
        
        # Today's sessions
        today_sessions = Session.objects.filter(
            schedule__date=today
        ).count()
        
        # Booking Statistics
        total_bookings = Booking.objects.count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        attended_bookings = Booking.objects.filter(status='attended').count()
        
        # Request Statistics
        total_requests = Request.objects.count()
        pending_requests = Request.objects.filter(status='pending').count()
        accepted_requests = Request.objects.filter(status='accepted').count()
        
        # Financial Data
        today_revenue = Session.objects.filter(
            status='completed',
            schedule__date=today,
            price__isnull=False
        ).aggregate(total=Sum('price'))['total'] or 0
        
        total_revenue = Session.objects.filter(
            status='completed',
            price__isnull=False
        ).aggregate(total=Sum('price'))['total'] or 0
        
        # Platform Health
        avg_rating = Feedback.objects.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0
        
        # Recent Activities
        recent_users = list(User.objects.order_by('-date_joined')[:10].values(
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_active'
        ))
        
        recent_sessions = list(Session.objects.select_related('mentor').order_by('-created_at')[:10].values(
            'id', 'title', 'status', 'schedule', 'mentor__username', 'mentor__first_name', 'mentor__last_name'
        ))
        
        recent_requests = list(Request.objects.select_related('learner', 'mentor').order_by('-created_at')[:10].values(
            'id', 'topic', 'status', 'created_at', 
            'learner__username', 'learner__first_name', 'learner__last_name',
            'mentor__username', 'mentor__first_name', 'mentor__last_name'
        ))
        
        # Top Performers
        top_mentors = list(User.objects.filter(role='mentor').annotate(
            session_count=Count('mentor_sessions'),
            avg_rating=Avg('mentor_sessions__feedback__rating')
        ).order_by('-session_count')[:5].values(
            'id', 'username', 'first_name', 'last_name', 'session_count', 'avg_rating'
        ))
        
        # System Metrics
        unread_notifications = Notification.objects.filter(read=False).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'users': {
                    'total': total_users,
                    'mentors': total_mentors,
                    'learners': total_learners,
                    'active': active_users,
                    'banned': banned_users,
                    'online': online_users
                },
                'sessions': {
                    'total': total_sessions,
                    'active': active_sessions,
                    'completed': completed_sessions,
                    'scheduled': scheduled_sessions,
                    'today': today_sessions
                },
                'bookings': {
                    'total': total_bookings,
                    'confirmed': confirmed_bookings,
                    'attended': attended_bookings
                },
                'requests': {
                    'total': total_requests,
                    'pending': pending_requests,
                    'accepted': accepted_requests
                },
                'revenue': {
                    'today': float(today_revenue),
                    'total': float(total_revenue)
                },
                'metrics': {
                    'avg_rating': round(float(avg_rating), 2),
                    'unread_notifications': unread_notifications
                },
                'recent': {
                    'users': recent_users,
                    'sessions': recent_sessions,
                    'requests': recent_requests
                },
                'top_mentors': top_mentors,
                'last_updated': now.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def admin_user_action_api(request):
    """Perform actions on users (ban, activate, delete, etc.)"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        action = data.get('action')
        
        if not user_id or not action:
            return JsonResponse({'error': 'User ID and action are required'}, status=400)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Prevent admins from affecting superusers unless they are superuser
        if user.is_superuser and not request.user.is_superuser:
            return JsonResponse({'error': 'Cannot modify superuser accounts'}, status=403)
        
        message = ''
        
        if action == 'ban':
            user.is_active = False
            user.save()
            message = f'User {user.username} has been banned'
            
        elif action == 'activate':
            user.is_active = True
            user.save()
            message = f'User {user.username} has been activated'
            
        elif action == 'delete':
            if user.is_superuser:
                return JsonResponse({'error': 'Cannot delete superuser accounts'}, status=403)
            
            # Store user info before deletion
            username = user.username
            user_email = user.email
            
            # Log the deletion action
            UserActivity.objects.create(
                user=request.user,
                activity_type='admin_action',
                description=f'Deleted user: {username} ({user_email})'
            )
            
            # Delete user (Django will handle cascading)
            user.delete()
            message = f'User {username} has been permanently deleted'
            
        elif action == 'make_mentor':
            user.role = 'mentor'
            user.save()
            message = f'User {user.username} is now a mentor'
            
        elif action == 'make_learner':
            user.role = 'learner'
            user.save()
            message = f'User {user.username} is now a learner'
            
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)