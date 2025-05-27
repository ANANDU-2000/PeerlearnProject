from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from users.models import User
from sessions.models import Session, Booking, Feedback
from recommendations.models import PopularityMetric
import json


@login_required
def admin_dashboard(request):
    """Main admin dashboard with comprehensive analytics"""
    
    # Check if user is admin/staff
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('login')  # Redirect non-admin users to login
    
    # Real-time metrics
    total_users = User.objects.count()
    total_mentors = User.objects.filter(role='mentor').count()
    total_learners = User.objects.filter(role='learner').count()
    pending_users = User.objects.filter(is_active=True).count()  # Adjust based on your verification field
    
    # Session metrics
    total_sessions = Session.objects.count()
    live_sessions = Session.objects.filter(status='live').count()
    scheduled_sessions = Session.objects.filter(status='scheduled').count()
    completed_sessions = Session.objects.filter(status='completed').count()
    
    # Revenue metrics
    today = timezone.now().date()
    # Calculate revenue based on confirmed bookings (₹500 per session)
    daily_bookings = Booking.objects.filter(
        created_at__date=today,
        status='confirmed'
    ).count()
    daily_revenue = daily_bookings * 500  # ₹500 per session
    
    monthly_bookings = Booking.objects.filter(
        created_at__month=today.month,
        created_at__year=today.year,
        status='confirmed'
    ).count()
    monthly_revenue = monthly_bookings * 500  # ₹500 per session
    
    # Growth calculations
    last_month = today.replace(month=today.month-1 if today.month > 1 else 12)
    last_month_users = User.objects.filter(
        date_joined__month=last_month.month,
        date_joined__year=last_month.year if today.month > 1 else today.year-1
    ).count()
    
    this_month_users = User.objects.filter(
        date_joined__month=today.month,
        date_joined__year=today.year
    ).count()
    
    user_growth = ((this_month_users - last_month_users) / max(last_month_users, 1)) * 100
    
    # System health metrics
    avg_rating = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    success_rate = (completed_sessions / max(total_sessions, 1)) * 100
    
    # Recent activity
    recent_bookings = Booking.objects.select_related('learner', 'session').order_by('-created_at')[:10]
    recent_sessions = Session.objects.select_related('mentor').order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Live sessions for display
    live_sessions_list = Session.objects.filter(status='live')[:6]
    
    # Add revenue calculation to sessions
    for session in recent_sessions:
        session_bookings = session.bookings.filter(status='confirmed')
        session.total_revenue = session_bookings.count() * 500  # ₹500 per confirmed booking
    
    context = {
        'total_users': total_users,
        'total_mentors': total_mentors,
        'total_learners': total_learners,
        'pending_users': pending_users,
        'total_sessions': total_sessions,
        'live_sessions': live_sessions,
        'live_sessions_list': live_sessions_list,
        'scheduled_sessions': scheduled_sessions,
        'completed_sessions': completed_sessions,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
        'user_growth': round(user_growth, 1),
        'avg_rating': round(avg_rating, 1),
        'success_rate': round(success_rate, 1),
        'recent_bookings': recent_bookings,
        'recent_sessions': recent_sessions,
        'recent_users': recent_users,
        'recent_sessions': recent_sessions,
        'recent_bookings': recent_bookings,
        'users': recent_users,  # For user management section
        'platform_fees': monthly_revenue * 0.1,  # 10% platform fee
        'notifications_count': 5,  # You can calculate real notifications later
    }
    
    return render(request, 'admin/real_dashboard.html', context)


@staff_member_required
@require_http_methods(["GET"])
def admin_users_api(request):
    """API endpoint for user management data"""
    
    # Get filter parameters
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # Build query
    users_query = User.objects.all()
    
    if search:
        users_query = users_query.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(skills__icontains=search)
        )
    
    if role_filter:
        users_query = users_query.filter(role=role_filter)
    
    if status_filter:
        if status_filter == 'active':
            users_query = users_query.filter(is_active=True, is_verified=True)
        elif status_filter == 'inactive':
            users_query = users_query.filter(is_active=False)
        elif status_filter == 'pending':
            users_query = users_query.filter(is_verified=False)
    
    # Paginate
    paginator = Paginator(users_query, page_size)
    users_page = paginator.get_page(page)
    
    # Build response data
    users_data = []
    for user in users_page:
        # Get user metrics
        if user.role == 'mentor':
            total_sessions = Session.objects.filter(mentor=user).count()
            total_earnings = Booking.objects.filter(
                session__mentor=user, 
                payment_status='completed'
            ).aggregate(total=Sum('amount_paid'))['total'] or 0
            total_spent = 0
        else:
            total_sessions = Booking.objects.filter(learner=user).count()
            total_earnings = 0
            total_spent = Booking.objects.filter(
                learner=user, 
                payment_status='completed'
            ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # Get average rating
        avg_rating = Feedback.objects.filter(
            session__mentor=user if user.role == 'mentor' else user
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Determine status
        if not user.is_verified:
            status = 'pending'
        elif not user.is_active:
            status = 'suspended'
        else:
            status = 'active'
        
        users_data.append({
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'role': user.role,
            'status': status,
            'total_sessions': total_sessions,
            'total_earnings': f"{total_earnings:,.0f}",
            'total_spent': f"{total_spent:,.0f}",
            'rating': f"{avg_rating:.1f}",
            'skills': user.skills or '',
            'last_active': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
            'join_date': user.date_joined.strftime('%Y-%m-%d'),
            'avatar': user.profile_image.url if user.profile_image else '/static/images/default-avatar.png',
            'is_online': (timezone.now() - user.last_login).seconds < 3600 if user.last_login else False
        })
    
    return JsonResponse({
        'users': users_data,
        'total_users': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': users_page.number,
        'has_next': users_page.has_next(),
        'has_previous': users_page.has_previous()
    })


@staff_member_required
@require_http_methods(["GET"])
def admin_live_sessions_api(request):
    """API endpoint for live session monitoring"""
    
    live_sessions = Session.objects.filter(status='live').select_related('mentor')
    
    sessions_data = []
    for session in live_sessions:
        # Get current participants
        current_participants = Booking.objects.filter(
            session=session, 
            status='confirmed'
        ).count()
        
        # Calculate session duration
        if session.schedule:
            duration_minutes = (timezone.now() - session.schedule).seconds // 60
            duration = f"{duration_minutes}m"
        else:
            duration = "Unknown"
        
        # Get session revenue
        revenue = Booking.objects.filter(
            session=session, 
            payment_status='completed'
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # Simulate quality metrics (in real implementation, this would come from WebRTC monitoring)
        quality = 85 + (hash(str(session.id)) % 15)  # Simulate 85-100% quality
        
        sessions_data.append({
            'id': session.id,
            'title': session.title,
            'mentor': session.mentor.get_full_name(),
            'participants': current_participants,
            'max_participants': session.max_participants,
            'duration': duration,
            'quality': quality,
            'revenue': f"{revenue:,.0f}"
        })
    
    return JsonResponse({
        'live_sessions': sessions_data,
        'total_live': len(sessions_data)
    })


@staff_member_required
@require_http_methods(["GET"])
def admin_analytics_api(request):
    """API endpoint for analytics data"""
    
    period = request.GET.get('period', '30')  # days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=int(period))
    
    # User growth data
    user_growth_data = []
    date_range = [start_date + timedelta(days=x) for x in range(int(period))]
    
    for date in date_range:
        users_count = User.objects.filter(date_joined__date=date).count()
        user_growth_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'users': users_count
        })
    
    # Revenue data
    revenue_data = []
    for date in date_range:
        daily_revenue = Booking.objects.filter(
            created_at__date=date,
            payment_status='completed'
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    
    # Session completion rates
    session_stats = Session.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled'))
    )
    
    completion_rate = (session_stats['completed'] / max(session_stats['total'], 1)) * 100
    
    return JsonResponse({
        'user_growth': user_growth_data,
        'revenue_data': revenue_data,
        'completion_rate': round(completion_rate, 1),
        'total_sessions': session_stats['total'],
        'completed_sessions': session_stats['completed'],
        'cancelled_sessions': session_stats['cancelled']
    })


@staff_member_required
@require_http_methods(["GET"])
def admin_live_activity_api(request):
    """API endpoint for real-time activity feed"""
    
    # Get recent activities from different models
    activities = []
    
    # Recent user registrations
    recent_users = User.objects.order_by('-date_joined')[:5]
    for user in recent_users:
        time_diff = timezone.now() - user.date_joined
        if time_diff.seconds < 3600:  # Last hour
            activities.append({
                'id': f"user_{user.id}",
                'type': 'user',
                'icon': 'fas fa-user-plus',
                'description': f'New {user.role} registered: {user.get_full_name()}',
                'time': get_time_ago(user.date_joined),
                'amount': None
            })
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('learner', 'session').order_by('-created_at')[:5]
    for booking in recent_bookings:
        time_diff = timezone.now() - booking.created_at
        if time_diff.seconds < 3600:  # Last hour
            activities.append({
                'id': f"booking_{booking.id}",
                'type': 'payment',
                'icon': 'fas fa-rupee-sign',
                'description': f'Payment received from {booking.learner.get_full_name()}',
                'time': get_time_ago(booking.created_at),
                'amount': f"{booking.amount_paid:,.0f}" if booking.amount_paid else None
            })
    
    # Recent session starts
    recent_sessions = Session.objects.filter(
        status='live',
        updated_at__gte=timezone.now() - timedelta(hours=1)
    ).select_related('mentor').order_by('-updated_at')[:5]
    
    for session in recent_sessions:
        activities.append({
            'id': f"session_{session.id}",
            'type': 'session',
            'icon': 'fas fa-play',
            'description': f'Session started: "{session.title}" by {session.mentor.get_full_name()}',
            'time': get_time_ago(session.updated_at),
            'amount': None
        })
    
    # Sort by most recent
    activities.sort(key=lambda x: x['time'], reverse=True)
    
    return JsonResponse({
        'activities': activities[:10]  # Return last 10 activities
    })


@staff_member_required
@require_http_methods(["POST"])
def admin_user_action(request):
    """Handle user management actions"""
    
    data = json.loads(request.body)
    action = data.get('action')
    user_id = data.get('user_id')
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        if action == 'suspend':
            user.is_active = False
            user.save()
            message = f"User {user.get_full_name()} has been suspended."
            
        elif action == 'activate':
            user.is_active = True
            user.save()
            message = f"User {user.get_full_name()} has been activated."
            
        elif action == 'verify':
            user.is_verified = True
            user.save()
            message = f"User {user.get_full_name()} has been verified."
            
        elif action == 'delete':
            user_name = user.get_full_name()
            user.delete()
            message = f"User {user_name} has been deleted."
            
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        
        return JsonResponse({'success': True, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_http_methods(["POST"])
def admin_session_action(request):
    """Handle session management actions"""
    
    data = json.loads(request.body)
    action = data.get('action')
    session_id = data.get('session_id')
    
    try:
        session = get_object_or_404(Session, id=session_id)
        
        if action == 'end':
            session.status = 'completed'
            session.save()
            message = f"Session '{session.title}' has been ended."
            
        elif action == 'cancel':
            session.status = 'cancelled'
            session.save()
            message = f"Session '{session.title}' has been cancelled."
            
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        
        return JsonResponse({'success': True, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_time_ago(timestamp):
    """Helper function to get human-readable time difference"""
    now = timezone.now()
    diff = now - timestamp
    
    if diff.seconds < 60:
        return "Just now"
    elif diff.seconds < 3600:
        minutes = diff.seconds // 60
        return f"{minutes} min ago"
    elif diff.days == 0:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "1 day ago"
    else:
        return f"{diff.days} days ago"


@staff_member_required
@require_http_methods(["GET"])
def admin_system_stats(request):
    """Get real-time system statistics"""
    
    # Calculate various metrics
    total_users = User.objects.count()
    online_users = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(minutes=30)
    ).count()
    
    active_sessions = Session.objects.filter(status='live').count()
    
    # System health simulation (in real app, this would check actual system metrics)
    system_health = 99.8
    
    # Today's revenue
    today_revenue = Booking.objects.filter(
        created_at__date=timezone.now().date(),
        payment_status='completed'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    return JsonResponse({
        'total_users': f"{total_users:,}",
        'online_users': f"{online_users:,}",
        'active_sessions': active_sessions,
        'system_health': system_health,
        'today_revenue': f"{today_revenue:,.0f}",
        'timestamp': timezone.now().isoformat()
    })