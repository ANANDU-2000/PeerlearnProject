from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .forms import UserRegistrationForm, UserProfileForm
from .models import User
from sessions.models import Session, Booking, Request
from recommendations.recommendation_engine import get_recommendations_for_user, get_mentor_recommendations_for_user

def landing_page(request):
    """Coursera-style landing page with ONLY future sessions and real mentors"""
    now = timezone.now()
    
    # Get ONLY future sessions with real mentors
    featured_sessions = Session.objects.filter(
        schedule__gte=now,
        status='scheduled',
        mentor__isnull=False
    ).select_related('mentor').distinct().order_by('schedule')[:6]
    
    # Get ONLY real mentors (no duplicates, with actual profiles)
    featured_mentors = User.objects.filter(
        role='mentor',
        first_name__isnull=False,
        last_name__isnull=False
    ).exclude(
        first_name='',
        last_name=''
    ).distinct()[:8]
    
    context = {
        'featured_sessions': featured_sessions,
        'featured_mentors': featured_mentors,
    }
    return render(request, 'landing_page.html', context)

def anandu_portfolio(request):
    """Premium portfolio page for Anandu Krishna - PeerLearn Founder"""
    return render(request, 'portfolio/anandu_portfolio.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        
        # Smart login detection: Admin/Owner -> Mentor -> Learner
        if user.is_superuser or user.is_staff:
            return reverse_lazy('admin_dashboard')
        elif user.role == 'mentor':
            return reverse_lazy('mentor_dashboard')
        else:
            return reverse_lazy('learner_dashboard')

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration/register_wizard.html'
    
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
        
        # Smart admin detection and redirection
        if user.is_staff or user.is_superuser:
            return redirect('/admin-dashboard/dashboard/')
        elif user.role == 'mentor':
            return redirect('mentor_dashboard')
        else:
            return redirect('learner_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.request.GET.get('role', 'learner')
        return context

def register_steps_view(request):
    """Enhanced step-by-step registration with profile image upload"""
    if request.method == 'GET':
        return render(request, 'registration/register_wizard.html')
    
    elif request.method == 'POST':
        try:
            # Get form data from wizard
            role = request.POST.get('role')
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password')
            password2 = request.POST.get('confirmPassword')
            
            # Optional fields from wizard
            skills = request.POST.get('skills', '')
            domains = request.POST.getlist('domains[]')  # Handle multiple domains
            expertise = ','.join(domains) if domains else ''
            bio = request.POST.get('bio', '')
            experience = request.POST.get('experience', '')
            profile_image = request.FILES.get('profile_image')
            
            # Validation
            if not all([role, first_name, last_name, username, email, password1, password2]):
                return JsonResponse({'success': False, 'error': 'All required fields must be filled'})
            
            if password1 != password2:
                return JsonResponse({'success': False, 'error': 'Passwords do not match'})
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'})
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'Email already registered'})
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role,
                skills=skills,
                interests=expertise,  # Using domains as interests
                domain=expertise,
                expertise=experience,
                bio=bio,
                career_goals=''  # Not collected in wizard
            )
            
            # Handle profile image upload
            if profile_image:
                user.profile_image = profile_image
                user.save()
            
            # Authenticate and login
            user = authenticate(username=username, password=password1)
            if user:
                login(request, user)
                
                # Smart admin detection and redirection
                if user.is_staff or user.is_superuser:
                    redirect_url = '/admin-dashboard/dashboard/'
                elif role == 'mentor':
                    redirect_url = '/dashboard/mentor/'
                else:
                    redirect_url = '/dashboard/learner/'
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Registration successful!',
                    'redirect_url': redirect_url
                })
            else:
                return JsonResponse({'success': False, 'error': 'Authentication failed'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def logout_view(request):
    """Handle logout for both GET and POST requests"""
    logout(request)
    return redirect('landing')

def admin_dashboard_redirect(request):
    """Redirect old admin dashboard URL to new working dashboard"""
    return redirect('/admin-dashboard/dashboard/')

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
    
    # Available sessions - Only FUTURE sessions with proper scheduling
    available_sessions = Session.objects.filter(
        status='scheduled',
        schedule__gt=timezone.now()  # Only future sessions
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
    
    # Get personalized recommendations using advanced ML engine
    try:
        recommended_sessions = get_recommendations_for_user(request.user)
        recommended_mentors = get_mentor_recommendations_for_user(request.user)
    except Exception as e:
        # Fallback to available sessions if recommendation engine fails
        recommended_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=timezone.now()
        ).exclude(
            bookings__learner=request.user,
            bookings__status='confirmed'
        ).select_related('mentor')[:6]
        recommended_mentors = []
    
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
        'recommended_mentors': recommended_mentors[:6] if recommended_mentors else [],
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


def check_username_api(request):
    """Real-time username availability check"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)
    
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Username must be at least 3 characters'})
    
    if len(username) > 30:
        return JsonResponse({'available': False, 'message': 'Username must be less than 30 characters'})
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({'available': False, 'message': 'Username already taken'})
    
    return JsonResponse({'available': True, 'message': 'Username is available'})

def check_email_api(request):
    """Real-time email availability check with smart detection"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
        except:
            email = request.POST.get('email', '').strip()
    else:
        email = request.GET.get('email', '').strip()
    
    email = email.lower()
    if not email:
        return JsonResponse({'available': False, 'message': 'Email is required'})
    
    # Basic email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({'available': False, 'message': 'Please enter a valid email address'})
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({'available': False, 'message': 'Email already registered'})
    
    return JsonResponse({'available': True, 'message': 'Email is available'})

@login_required
def admin_dashboard(request):
    """Advanced admin dashboard with owner privileges for Anandu Krishna"""
    # Only allow superusers/staff (admins)
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('learner_dashboard')
    
    from django.contrib.auth import get_user_model
    from sessions.models import Session, Booking, Feedback
    from django.db.models import Count, Avg, Q
    from datetime import datetime, timedelta
    
    User = get_user_model()
    
    # Platform Analytics
    total_users = User.objects.count()
    total_mentors = User.objects.filter(role='mentor').count()
    total_learners = User.objects.filter(role='learner').count()
    total_sessions = Session.objects.count()
    total_bookings = Booking.objects.count()
    
    # Recent Activities
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_sessions = Session.objects.order_by('-created_at')[:10]
    recent_bookings = Booking.objects.order_by('-created_at')[:10]
    
    # Online Users (active in last 30 minutes)
    thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
    online_users = User.objects.filter(last_login__gte=thirty_minutes_ago)
    
    # Performance Metrics
    avg_rating = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    completion_rate = Booking.objects.filter(status='completed').count() / max(total_bookings, 1) * 100
    
    # Top Performers
    top_mentors = User.objects.filter(role='mentor').annotate(
        session_count=Count('mentor_sessions'),
        avg_rating=Avg('mentor_sessions__feedback__rating')
    ).order_by('-session_count')[:5]
    
    context = {
        'total_users': total_users,
        'total_mentors': total_mentors,
        'total_learners': total_learners,
        'total_sessions': total_sessions,
        'total_bookings': total_bookings,
        'recent_users': recent_users,
        'recent_sessions': recent_sessions,
        'recent_bookings': recent_bookings,
        'online_users': online_users,
        'online_count': online_users.count(),
        'avg_rating': round(avg_rating, 2),
        'completion_rate': round(completion_rate, 2),
        'top_mentors': top_mentors,
        'is_owner': request.user.is_superuser,
    }
    
    return render(request, 'dashboard/admin_complete.html', context)
