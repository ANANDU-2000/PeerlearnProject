from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from sessions.models import Session, Booking, Feedback
from users.models import User
from .models import PopularityMetric
from .recommendation_engine import get_recommendations_for_user, get_mentor_recommendations_for_user

@login_required
def recommendations_page(request):
    """Dedicated recommendations page with advanced ML engine"""
    
    # Get personalized recommendations
    try:
        recommended_sessions = get_recommendations_for_user(request.user)
        recommended_mentors = get_mentor_recommendations_for_user(request.user)
    except Exception as e:
        # Fallback to showing available sessions
        recommended_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=timezone.now()
        ).exclude(
            bookings__learner=request.user,
            bookings__status='confirmed'
        ).select_related('mentor')[:8]
        recommended_mentors = []
    
    # Get trending sessions (last 7 days activity)
    from datetime import timedelta
    recent_date = timezone.now() - timedelta(days=7)
    trending_sessions = Session.objects.filter(
        status='scheduled',
        schedule__gte=timezone.now(),
        bookings__created_at__gte=recent_date
    ).exclude(
        bookings__learner=request.user,
        bookings__status='confirmed'
    ).annotate(
        recent_bookings=Count('bookings', filter=Q(bookings__created_at__gte=recent_date))
    ).filter(recent_bookings__gte=1).order_by('-recent_bookings')[:5]
    
    # Get popular sessions with ratings
    popular_sessions = Session.objects.filter(
        status='scheduled',
        schedule__gte=timezone.now(),
        popularity__isnull=False
    ).exclude(
        bookings__learner=request.user,
        bookings__status='confirmed'
    ).select_related('popularity', 'mentor').order_by(
        '-popularity__rating_average',
        '-popularity__booking_count'
    )[:5]
    
    # Get all available sessions as backup
    all_sessions = Session.objects.filter(
        status='scheduled',
        schedule__gte=timezone.now()
    ).exclude(
        bookings__learner=request.user,
        bookings__status='confirmed'
    ).select_related('mentor')[:10]
    
    context = {
        'recommended_sessions': recommended_sessions,
        'recommended_mentors': recommended_mentors,
        'trending_sessions': trending_sessions,
        'popular_sessions': popular_sessions,
        'all_sessions': all_sessions,
        'user_skills': request.user.skills or '',
        'user_expertise': request.user.expertise or ''
    }
    
    return render(request, 'recommendations/recommendations_page.html', context)

@login_required
def trending_sessions(request):
    """Get trending sessions based on popularity metrics"""
    from datetime import timedelta
    recent_date = timezone.now() - timedelta(days=7)
    
    trending = Session.objects.filter(
        status='scheduled',
        schedule__gte=timezone.now(),
        bookings__created_at__gte=recent_date
    ).exclude(
        bookings__learner=request.user,
        bookings__status='confirmed'
    ).annotate(
        recent_bookings=Count('bookings', filter=Q(bookings__created_at__gte=recent_date)),
        avg_rating=Avg('feedback__rating')
    ).filter(recent_bookings__gte=1).order_by('-recent_bookings', '-avg_rating')
    
    data = []
    for session in trending:
        data.append({
            'id': session.id,
            'title': session.title,
            'description': session.description,
            'mentor': session.mentor.first_name,
            'price': float(session.price) if session.price else 0,
            'schedule': session.schedule.isoformat(),
            'recent_bookings': session.recent_bookings,
            'rating': float(session.avg_rating) if session.avg_rating else 0
        })
    
    return JsonResponse({'trending_sessions': data})

@login_required 
def recommended_sessions(request):
    """Get personalized recommendations for the user"""
    try:
        recommendations = get_recommendations_for_user(request.user)
        data = []
        for session in recommendations:
            data.append({
                'id': session.id,
                'title': session.title,
                'description': session.description,
                'mentor': session.mentor.first_name,
                'price': float(session.price) if session.price else 0,
                'schedule': session.schedule.isoformat(),
                'reason': 'AI Recommended based on your profile'
            })
        return JsonResponse({'recommended_sessions': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def update_session_popularity(session_id, action):
    """Helper function to update popularity metrics"""
    try:
        session = Session.objects.get(id=session_id)
        popularity, created = PopularityMetric.objects.get_or_create(session=session)
        
        if action == 'view':
            popularity.view_count += 1
        elif action == 'book':
            popularity.booking_count += 1
        
        popularity.save()
    except:
        pass