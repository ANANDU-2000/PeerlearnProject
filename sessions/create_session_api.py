from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Session

@login_required 
@require_http_methods(["POST"])
def create_session_api(request):
    """Create session from modal form - Real Database Implementation"""
    if request.user.role != 'mentor':
        messages.error(request, 'Only mentors can create sessions')
        return redirect('mentor_dashboard')
    
    try:
        # Get real form data from modal
        title = request.POST.get('title')
        description = request.POST.get('description') 
        schedule_str = request.POST.get('schedule')
        duration = int(request.POST.get('duration', 60))
        max_participants = int(request.POST.get('max_participants', 10))
        status = request.POST.get('status', 'draft')
        
        # CRITICAL: Handle pricing data from your form
        session_type = request.POST.get('session_type', 'free')
        price = None
        
        # Process your entered price (₹200)
        if session_type == 'paid':
            price_value = request.POST.get('price')
            if price_value and price_value.strip():
                try:
                    price = float(price_value)
                except ValueError:
                    messages.error(request, 'Invalid price format')
                    return redirect('mentor_dashboard')
        
        # Parse and validate schedule
        schedule = datetime.strptime(schedule_str, '%Y-%m-%dT%H:%M')
        if timezone.is_naive(schedule):
            schedule = timezone.make_aware(schedule)
            
        # Validate future date
        if schedule <= timezone.now():
            messages.error(request, 'Session must be scheduled for a future date and time')
            return redirect('mentor_dashboard')
        
        # Create session with real database save INCLUDING PRICE
        session = Session.objects.create(
            mentor=request.user,
            title=title.strip(),
            description=description.strip(),
            schedule=schedule,
            duration=duration,
            max_participants=max_participants,
            status=status,
            price=price  # CRITICAL: Save your ₹200 price here
        )
        
        # Success message with real status
        if status == 'scheduled':
            messages.success(request, f'🎉 Session "{title}" created and published successfully! Learners can now book it.')
        else:
            messages.success(request, f'✓ Session "{title}" saved as draft. You can publish it later.')
            
        return redirect('mentor_dashboard')
        
    except ValueError as e:
        messages.error(request, 'Invalid date format. Please select a valid date and time.')
        return redirect('mentor_dashboard')
    except Exception as e:
        messages.error(request, f'Error creating session: {str(e)}')
        return redirect('mentor_dashboard')