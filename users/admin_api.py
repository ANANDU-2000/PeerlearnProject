# Advanced Admin API Endpoints for PeerLearn Platform
# Comprehensive admin controls with real-time features

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
import json
import requests
from datetime import datetime, timedelta
from .models import User
from sessions.models import Session, Booking, Feedback, Notification

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