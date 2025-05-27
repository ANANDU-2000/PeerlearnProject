from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@require_http_methods(["GET"])
def check_email_exists(request):
    """Check if email already exists in database - live validation"""
    email = request.GET.get('email', '').strip().lower()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email is required'})
    
    # Basic email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({'available': False, 'message': 'Please enter a valid email address'})
    
    # Check if email exists in database
    exists = User.objects.filter(email__iexact=email).exists()
    
    if exists:
        return JsonResponse({'available': False, 'message': 'Email already registered'})
    else:
        return JsonResponse({'available': True, 'message': 'Email is available'})