from django.shortcuts import render, redirect, get_object_or_404
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
from .forms import UserRegistrationForm, UserProfileForm, ProfileForm
from .models import User
from sessions.models import Session, Booking, Request
from recommendations.recommendation_engine import get_recommendations_for_user, get_mentor_recommendations_for_user
from django.db.models import Count, Avg, Q, Sum

def landing_page(request):
    """Coursera-style landing page with ONLY future sessions and real mentors"""
    from django.contrib.auth import get_user_model
    from sessions.models import Session
    User = get_user_model()
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

    # Add stats for template
    total_users = User.objects.count()
    total_mentors = User.objects.filter(role='mentor').count()
    total_sessions = Session.objects.count()
    online_count = 0  # Replace with real online user tracking if available

    context = {
        'featured_sessions': featured_sessions,
        'featured_mentors': featured_mentors,
        'total_users': total_users,
        'total_mentors': total_mentors,
        'total_sessions': total_sessions,
        'online_count': online_count,
    }
    return render(request, 'landing_page.html', context)

def anandu_portfolio(request):
    """Premium portfolio page for Anandu Krishna - PeerLearn Founder"""
    return render(request, 'portfolio/anandu_portfolio.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Override to redirect admin users to enhanced dashboard"""
        response = super().form_valid(form)
        user = self.request.user
        
        # Check if user is admin/staff and redirect to enhanced dashboard
        if user.is_staff or user.is_superuser:
            return redirect('/admin-dashboard/dashboard/')
        
        # Regular users go to their role-based dashboards
        if user.role == 'mentor':
            return redirect('/dashboard/mentor/')
        elif user.role == 'learner':
            return redirect('/dashboard/learner/')
        
        return response
    
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
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile_view')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileForm(instance=user)

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'profile/advanced.html', context)

@login_required
def advanced_profile_view(request):
    """Advanced profile view with comprehensive features"""
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile/advanced.html', context)

@login_required
def mentor_dashboard(request):
    """Enhanced mentor dashboard with real-time data and advanced features"""
    user = request.user
    
    # Check if user profile is complete
    if not user.is_mentor:
        return redirect('learner_dashboard')
    
    # Check if profile is complete (basic check)
    profile_complete = bool(user.first_name and user.last_name and user.bio)
    if not profile_complete:
        messages.warning(request, 'Please complete your profile before accessing the dashboard.')
        return redirect('profile_view')
    
    now = timezone.now()
    
    # Get all sessions for this mentor
    all_sessions = Session.objects.filter(mentor=user).order_by('-created_at')
    
    # Get draft sessions
    draft_sessions = all_sessions.filter(status='draft')
    
    # Get upcoming sessions
    upcoming_sessions = all_sessions.filter(
        schedule__gte=now,
        status='scheduled'
    ).select_related('learner').order_by('schedule')
    
    # Get past sessions for history
    past_sessions = all_sessions.filter(
        schedule__lt=now
    ).select_related('learner').order_by('-schedule')[:5]
    
    # Get pending requests
    pending_requests = Request.objects.filter(
        mentor=user,
        status='pending'
    ).select_related('learner').order_by('-created_at')
    
    # Get session statistics
    total_sessions = all_sessions.count()
    completed_sessions = all_sessions.filter(status='completed').count()
    upcoming_count = upcoming_sessions.count()
    draft_count = draft_sessions.count()
    
    # Get earnings data
    total_earnings = all_sessions.filter(
        status='completed'
    ).aggregate(total=Sum('price'))['total'] or 0
    
    context = {
        'user': user,
        'all_sessions': all_sessions,
        'draft_sessions': draft_sessions,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'pending_requests': pending_requests,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'upcoming_count': upcoming_count,
        'draft_count': draft_count,
        'total_earnings': total_earnings,
    }
    
    return render(request, 'dashboard/mentor_complete.html', context)

@login_required
def learner_dashboard(request):
    """Enhanced learner dashboard with real-time data and advanced features"""
    user = request.user
    
    # Check if user profile is complete
    if not user.is_learner:
        return redirect('mentor_dashboard')
    
    # Check if profile is complete (basic check)
    profile_complete = bool(user.first_name and user.last_name and user.bio)
    if not profile_complete:
        messages.warning(request, 'Please complete your profile before accessing the dashboard.')
        return redirect('profile_view')
    
    now = timezone.now()
    
    # Get upcoming sessions through bookings
    upcoming_sessions = Session.objects.filter(
        bookings__learner=user,
        status='scheduled'
    ).select_related('mentor').order_by('schedule')
    
    # Get past sessions for history
    past_sessions = Session.objects.filter(
        bookings__learner=user,
        status='completed'
    ).select_related('mentor').order_by('-schedule')[:5]
    
    # Get pending requests
    pending_requests = Request.objects.filter(
        learner=user,
        status='pending'
    ).select_related('mentor').order_by('-created_at')
    
    # Get available sessions
    available_sessions = Session.objects.filter(
        status='scheduled'
    ).exclude(
        bookings__learner=user,
        bookings__status='confirmed'
    ).select_related('mentor').order_by('schedule')
    
    # Get available mentors - FIXED: Show ALL active mentors, don't exclude previous ones
    available_mentors = User.objects.filter(
        role='mentor',
        is_active=True,
        first_name__isnull=False,
        last_name__isnull=False
    ).exclude(
        first_name='',
        last_name=''
    ).order_by('-date_joined')  # Show newest mentors first
    
    # Get recommended mentors based on skills and expertise
    user_skills = [skill.strip().lower() for skill in (user.skills or '').split(',') if skill.strip()]
    user_interests = [interest.strip().lower() for interest in (user.interests or '').split(',') if interest.strip()]
    
    recommended_mentors = User.objects.filter(
        role='mentor',
        is_active=True,
        first_name__isnull=False,
        last_name__isnull=False
    ).exclude(
        first_name='',
        last_name=''
    )
    
    # Filter recommended mentors by user's domain and interests
    if user.domain:
        recommended_mentors = recommended_mentors.filter(
            Q(skills__icontains=user.domain) |
            Q(interests__icontains=user.domain) |
            Q(domain__icontains=user.domain)
        )
    if user.interests:
        for interest in user_interests:
            if interest:
                recommended_mentors = recommended_mentors.filter(
                    Q(skills__icontains=interest) |
                    Q(interests__icontains=interest)
                )
    
    recommended_mentors = recommended_mentors.distinct()[:6]
    
    # ENHANCED: Get ALL pending requests - both sent and received
    pending_requests = Request.objects.filter(
        Q(learner=user) | Q(mentor=user),
        status='pending'
    ).select_related('learner', 'mentor').order_by('-created_at')
    
    # Get accepted/responded requests for acknowledgments
    responded_requests = Request.objects.filter(
        learner=user,
        status__in=['accepted', 'declined']
    ).select_related('mentor').order_by('-updated_at')[:10]
    
    # FIXED: Add Recommendations Data for Subtabs
    # Get AI-recommended sessions based on user's interests and domain
    ai_recommended_sessions = Session.objects.filter(
        status='scheduled'
    ).exclude(
        bookings__learner=user,
        bookings__status='confirmed'
    ).select_related('mentor')
    
    # Filter by user interests and domain if available
    if user.domain:
        ai_recommended_sessions = ai_recommended_sessions.filter(
            Q(title__icontains=user.domain) |
            Q(description__icontains=user.domain) |
            Q(category__icontains=user.domain)
        )
    if user.interests:
        interest_keywords = [interest.strip() for interest in user.interests.split(',')]
        for keyword in interest_keywords:
            if keyword:
                ai_recommended_sessions = ai_recommended_sessions.filter(
                    Q(title__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(skills__icontains=keyword)
                )
    
    ai_recommended_sessions = ai_recommended_sessions.order_by('-created_at')[:8]
    
    # Get popular sessions (most bookings)
    popular_sessions = Session.objects.filter(
        status='scheduled'
    ).exclude(
        bookings__learner=user,
        bookings__status='confirmed'
    ).select_related('mentor').annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:8]
    
    # Get new sessions (recently created)
    new_sessions = Session.objects.filter(
        status='scheduled'
    ).exclude(
        bookings__learner=user,
        bookings__status='confirmed'
    ).select_related('mentor').order_by('-created_at')[:8]
    
    # Get session statistics
    total_sessions = Session.objects.filter(bookings__learner=user).count()
    completed_sessions = Session.objects.filter(
        bookings__learner=user,
        status='completed'
    ).count()
    upcoming_count = upcoming_sessions.count()
    
    # Calculate stats
    stats = {
        'attended_sessions': completed_sessions,
        'total_hours': sum(session.duration for session in past_sessions) // 60,
        'unique_mentors': Session.objects.filter(
            bookings__learner=user,
            bookings__status='confirmed'
        ).values('mentor').distinct().count()
    }
    
    context = {
        'user': user,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'pending_requests': pending_requests,
        'available_sessions': available_sessions,
        'available_mentors': available_mentors,
        'recommended_mentors': recommended_mentors,
        'responded_requests': responded_requests,
        # FIXED: Added recommendations data for subtabs
        'recommended_sessions': ai_recommended_sessions,
        'popular_sessions': popular_sessions,
        'new_sessions': new_sessions,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'upcoming_count': upcoming_count,
        'stats': stats,
        'user_bookings': upcoming_sessions,  # For the template's booking count
        'user_requests': pending_requests,   # For the template's request count
        'now': now,  # For time comparisons in template
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

def mentor_profile_view(request, mentor_id):
    """Public mentor profile view"""
    mentor = get_object_or_404(User, id=mentor_id, role='mentor')
    
    # Get mentor's sessions for display
    mentor_sessions = Session.objects.filter(
        mentor=mentor,
        status='scheduled'
    ).order_by('schedule')[:5]
    
    # Get mentor's completed sessions count
    completed_sessions = Session.objects.filter(
        mentor=mentor,
        status='completed'
    ).count()
    
    # Calculate average rating (placeholder for now)
    average_rating = 4.8
    
    context = {
        'mentor': mentor,
        'mentor_sessions': mentor_sessions,
        'completed_sessions': completed_sessions,
        'average_rating': average_rating,
    }
    
    return render(request, 'mentors/profile.html', context)
