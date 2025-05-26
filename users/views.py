from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .forms import UserRegistrationForm, UserProfileForm
from .models import User

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_mentor:
            return reverse_lazy('mentor_dashboard')
        else:
            return reverse_lazy('learner_dashboard')

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration/register_working.html'
    
    def get_initial(self):
        initial = super().get_initial()
        role = self.request.GET.get('role', 'learner')
        if role in ['mentor', 'learner']:
            initial['role'] = role
        return initial
    
    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, 'Registration successful!')
        
        if user.is_mentor:
            return redirect('mentor_dashboard')
        else:
            return redirect('learner_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.request.GET.get('role', 'learner')
        return context

def logout_view(request):
    """Handle logout for both GET and POST requests"""
    logout(request)
    return redirect('landing')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Calculate profile statistics based on user role
    if request.user.is_mentor:
        from sessions.models import Session
        completed_sessions_count = Session.objects.filter(
            mentor=request.user, 
            status='completed'
        ).count()
        confirmed_bookings_count = 0
    else:
        from sessions.models import Booking
        completed_sessions_count = 0
        confirmed_bookings_count = Booking.objects.filter(
            learner=request.user, 
            status='confirmed'
        ).count()
    
    context = {
        'form': form,
        'completed_sessions_count': completed_sessions_count,
        'confirmed_bookings_count': confirmed_bookings_count,
    }
    
    return render(request, 'profile.html', context)

@login_required
def mentor_dashboard(request):
    if request.user.role != 'mentor':
        messages.error(request, 'Access denied. Mentor role required.')
        return redirect('learner_dashboard')
    
    # Get mentor's sessions
    from sessions.models import Session, Booking, Request
    from django.db.models import Count, Avg, Q
    from django.utils import timezone
    
    # Sessions data
    mentor_sessions = Session.objects.filter(mentor=request.user).order_by('-schedule')
    
    # Requests data
    pending_requests = Request.objects.filter(
        status='pending',
        domain__in=request.user.expertise or []
    ).order_by('-created_at')
    
    # Analytics data
    total_sessions = mentor_sessions.count()
    total_students = Booking.objects.filter(
        session__mentor=request.user,
        status='confirmed'
    ).values('learner').distinct().count()
    
    avg_rating = mentor_sessions.filter(
        feedback__isnull=False
    ).aggregate(avg_rating=Avg('feedback__rating'))['avg_rating'] or 0
    
    # Earnings calculation (placeholder - implement with payment system)
    total_earnings = 0
    for session in mentor_sessions.filter(status='completed'):
        total_earnings += (session.bookings.filter(status='confirmed').count() * 50)  # Example rate
    
    context = {
        'mentor_sessions': mentor_sessions[:10],  # Recent sessions
        'pending_requests': pending_requests[:5],
        'total_sessions': total_sessions,
        'total_students': total_students,
        'avg_rating': round(avg_rating, 1),
        'total_earnings': total_earnings,
        'upcoming_sessions': mentor_sessions.filter(
            schedule__gte=timezone.now(),
            status='scheduled'
        ).count()
    }
    
    return render(request, 'dashboard/mentor_complete.html', context)

@login_required
def learner_dashboard(request):
    if request.user.role != 'learner':
        messages.error(request, 'Access denied. Learner role required.')
        return redirect('mentor_dashboard')
    
    # Get learner's data
    from sessions.models import Session, Booking, Request, Feedback
    from recommendations.models import PopularityMetric
    from django.db.models import Q
    from django.utils import timezone
    
    # Available sessions
    available_sessions = Session.objects.filter(
        status='scheduled',
        schedule__gte=timezone.now()
    ).exclude(
        bookings__learner=request.user,
        bookings__status='confirmed'
    ).order_by('schedule')[:10]
    
    # User's bookings
    user_bookings = Booking.objects.filter(
        learner=request.user,
        status='confirmed'
    ).select_related('session').order_by('-session__schedule')
    
    # User's requests
    user_requests = Request.objects.filter(
        learner=request.user
    ).order_by('-created_at')
    
    # Enhanced Recommended sessions with popularity metrics
    user_interests = request.user.expertise or []
    recommended_sessions = Session.objects.filter(
        status='scheduled',
        schedule__gte=timezone.now()
    ).exclude(
        bookings__learner=request.user,
        bookings__status='confirmed'
    ).select_related('mentor', 'popularity').order_by('-popularity__rating_average', '-popularity__booking_count')[:10]
    
    # If no recommendations from popularity, use interest-based
    if not recommended_sessions.exists() and user_interests:
        recommended_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=timezone.now(),
            description__icontains=user_interests[0] if user_interests else ''
        ).exclude(
            bookings__learner=request.user,
            bookings__status='confirmed'
        )[:5]
    
    # Learning stats
    attended_sessions = Feedback.objects.filter(user=request.user).count()
    total_hours = sum([
        booking.session.duration for booking in user_bookings 
        if booking.session.status == 'completed'
    ]) // 60  # Convert to hours
    unique_mentors = user_bookings.values('session__mentor').distinct().count()
    
    context = {
        'available_sessions': available_sessions,
        'user_bookings': user_bookings[:5],
        'user_requests': user_requests[:5],
        'recommended_sessions': recommended_sessions[:6],
        'stats': {
            'attended_sessions': attended_sessions,
            'total_hours': total_hours,
            'unique_mentors': unique_mentors
        }
    }
    
    return render(request, 'dashboard/learner_complete.html', context)


@login_required
@require_http_methods(["POST"])
def update_profile_api(request):
    """Update user profile via API"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Update user fields
        if 'bio' in data:
            user.bio = data['bio']
        if 'skills' in data:
            user.skills = data['skills']
        if 'hourly_rate' in data and user.is_mentor:
            user.hourly_rate = data['hourly_rate']
            
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
