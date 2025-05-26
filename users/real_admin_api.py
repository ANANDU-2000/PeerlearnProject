from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from sessions.models import Session, Booking, Feedback
from datetime import timedelta
import json

User = get_user_model()

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'User {user.username} status updated to {"Active" if user.is_active else "Inactive"}',
            'new_status': user.is_active
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_real_stats(request):
    """Get real-time platform statistics"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        # Real user counts
        total_users = User.objects.count()
        total_mentors = User.objects.filter(role='mentor').count()
        total_learners = User.objects.filter(role='learner').count()
        
        # Real online users (active in last 15 minutes)
        fifteen_minutes_ago = timezone.now() - timedelta(minutes=15)
        online_count = User.objects.filter(last_login__gte=fifteen_minutes_ago).count()
        
        # Real session data
        total_sessions = Session.objects.count()
        active_sessions = Session.objects.filter(status='live').count()
        scheduled_sessions = Session.objects.filter(status='scheduled').count()
        completed_sessions = Session.objects.filter(status='completed').count()
        
        # Real booking data
        total_bookings = Booking.objects.count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        
        # Real revenue calculation
        completed_sessions_with_price = Session.objects.filter(
            status='completed', 
            price__isnull=False
        )
        total_revenue = sum([float(session.price) for session in completed_sessions_with_price if session.price])
        
        today = timezone.now().date()
        today_revenue = sum([
            float(session.price) for session in completed_sessions_with_price.filter(
                updated_at__date=today
            ) if session.price
        ])
        
        # Real feedback stats
        total_feedback = Feedback.objects.count()
        avg_rating = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        return JsonResponse({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'mentors': total_mentors,
                    'learners': total_learners,
                    'online': online_count
                },
                'sessions': {
                    'total': total_sessions,
                    'active': active_sessions,
                    'scheduled': scheduled_sessions,
                    'completed': completed_sessions
                },
                'bookings': {
                    'total': total_bookings,
                    'confirmed': confirmed_bookings,
                    'pending': pending_bookings
                },
                'revenue': {
                    'total': round(total_revenue, 2),
                    'today': round(today_revenue, 2)
                },
                'feedback': {
                    'total': total_feedback,
                    'avg_rating': round(avg_rating, 2)
                }
            },
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_real_users(request):
    """Get real user list with pagination"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        search = request.GET.get('search', '')
        role_filter = request.GET.get('role', '')
        
        # Build query
        users_query = User.objects.all()
        
        if search:
            users_query = users_query.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if role_filter:
            users_query = users_query.filter(role=role_filter)
        
        users_query = users_query.order_by('-date_joined')
        
        # Paginate
        paginator = Paginator(users_query, per_page)
        users_page = paginator.get_page(page)
        
        users_data = []
        for user in users_page:
            users_data.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'role': user.role,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': users_page.has_next(),
                'has_previous': users_page.has_previous(),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_real_sessions(request):
    """Get real session list"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        sessions = Session.objects.all().order_by('-created_at')[:50]
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'mentor': {
                    'username': session.mentor.username,
                    'email': session.mentor.email
                },
                'status': session.status,
                'schedule': session.schedule.isoformat() if session.schedule else None,
                'price': float(session.price) if session.price else 0,
                'max_participants': session.max_participants,
                'current_participants': session.bookings.filter(status='confirmed').count(),
                'created_at': session.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_real_bookings(request):
    """Get real booking list"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        bookings = Booking.objects.all().order_by('-created_at')[:50]
        
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                'id': str(booking.id),
                'learner': {
                    'username': booking.learner.username,
                    'email': booking.learner.email
                },
                'session': {
                    'title': booking.session.title,
                    'mentor': booking.session.mentor.username
                },
                'status': booking.status,
                'created_at': booking.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'bookings': bookings_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_user(request, user_id):
    """Update user information"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        data = json.loads(request.body)
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'User {user.username} updated successfully'
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_real_activity(request):
    """Get real recent activity"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        activities = []
        
        # Recent user registrations
        recent_users = User.objects.order_by('-date_joined')[:5]
        for user in recent_users:
            activities.append({
                'type': 'user_registered',
                'message': f'New user registered: {user.username}',
                'timestamp': user.date_joined.isoformat(),
                'icon': 'fas fa-user-plus',
                'status': 'success'
            })
        
        # Recent sessions
        recent_sessions = Session.objects.order_by('-created_at')[:5]
        for session in recent_sessions:
            activities.append({
                'type': 'session_created',
                'message': f'New session: {session.title} by {session.mentor.username}',
                'timestamp': session.created_at.isoformat(),
                'icon': 'fas fa-video',
                'status': 'info'
            })
        
        # Recent bookings
        recent_bookings = Booking.objects.order_by('-created_at')[:5]
        for booking in recent_bookings:
            activities.append({
                'type': 'booking_created',
                'message': f'{booking.learner.username} booked {booking.session.title}',
                'timestamp': booking.created_at.isoformat(),
                'icon': 'fas fa-calendar-check',
                'status': 'success'
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'activities': activities[:20]  # Return last 20 activities
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)