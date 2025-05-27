from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login
from django.db import transaction
import json
import re
from .models import User

@csrf_exempt
@require_http_methods(["POST"])
def advanced_registration_api(request):
    """Advanced registration API with full validation and user creation"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'{field.replace("_", " ").title()} is required'
                })
        
        # Email validation
        email = data['email'].lower().strip()
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'An account with this email already exists'
            })
        
        # Email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid email address'
            })
        
        # Password validation
        password = data['password']
        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            })
        
        # Name validation
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        if len(first_name) < 2 or len(last_name) < 2:
            return JsonResponse({
                'success': False,
                'error': 'First and last names must be at least 2 characters long'
            })
        
        # Role validation
        role = data['role']
        if role not in ['learner', 'mentor']:
            return JsonResponse({
                'success': False,
                'error': 'Please select a valid role'
            })
        
        # Skills validation
        skills = data.get('skills', [])
        if len(skills) == 0:
            return JsonResponse({
                'success': False,
                'error': 'Please add at least one skill'
            })
        
        # Create username from email
        username = email.split('@')[0]
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Create user and profile in transaction
        with transaction.atomic():
            # Create Django user with all fields
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                skills=', '.join(skills),  # Store as comma-separated string
                interests=data.get('interests', ''),
                domain=data.get('primary_domain', ''),
                expertise=data.get('primary_domain', ''),
                location=data.get('country', '')
            )
            
            # Auto-login the user
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                
                # Determine redirect URL based on role
                if role == 'mentor':
                    redirect_url = '/dashboard/mentor/'
                else:
                    redirect_url = '/dashboard/learner/'
                
                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful! Welcome to PeerLearn!',
                    'redirect_url': redirect_url,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': role
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Registration completed but login failed. Please try logging in manually.'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        })

@require_http_methods(["GET"])
def check_email_availability(request):
    """Check if email is available for registration"""
    email = request.GET.get('email', '').lower().strip()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email is required'})
    
    # Email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({'available': False, 'message': 'Invalid email format'})
    
    # Check if email exists
    is_available = not User.objects.filter(email=email).exists()
    
    return JsonResponse({
        'available': is_available,
        'message': 'Email is available' if is_available else 'Email is already registered'
    })

@require_http_methods(["GET"])
def get_skill_suggestions(request):
    """Get skill suggestions based on domain"""
    domain = request.GET.get('domain', '')
    search_term = request.GET.get('search', '').lower()
    
    skill_database = {
        'technology': [
            'JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'AWS', 'Docker', 'Git', 
            'TypeScript', 'MongoDB', 'Django', 'Flask', 'Vue.js', 'Angular', 'PHP',
            'Java', 'C++', 'Machine Learning', 'Data Science', 'DevOps', 'Kubernetes',
            'REST APIs', 'GraphQL', 'Redis', 'PostgreSQL', 'MySQL', 'Linux', 'CI/CD'
        ],
        'business': [
            'Project Management', 'Leadership', 'Strategy', 'Analytics', 'Sales', 
            'Marketing', 'Operations', 'Finance', 'Business Development', 'Consulting',
            'Team Management', 'Product Management', 'Agile', 'Scrum', 'Negotiation',
            'Communication', 'Presentation Skills', 'Strategic Planning'
        ],
        'design': [
            'UI/UX Design', 'Figma', 'Adobe Creative Suite', 'Prototyping', 'User Research', 
            'Wireframing', 'Photoshop', 'Illustrator', 'Sketch', 'InVision', 'Principle',
            'After Effects', 'Web Design', 'Mobile Design', 'Brand Design', 'Typography'
        ],
        'marketing': [
            'Digital Marketing', 'SEO', 'Content Marketing', 'Social Media', 'PPC', 
            'Email Marketing', 'Analytics', 'Google Ads', 'Facebook Ads', 'Instagram Marketing',
            'LinkedIn Marketing', 'Influencer Marketing', 'Brand Strategy', 'Copywriting'
        ],
        'finance': [
            'Financial Analysis', 'Investment', 'Accounting', 'Risk Management', 'Excel', 
            'Financial Modeling', 'Corporate Finance', 'Personal Finance', 'Trading',
            'Portfolio Management', 'Financial Planning', 'Budgeting', 'Tax Planning'
        ],
        'health': [
            'Nutrition', 'Fitness', 'Mental Health', 'Yoga', 'Meditation', 'Wellness Coaching',
            'Personal Training', 'Diet Planning', 'Stress Management', 'Mindfulness',
            'Health Coaching', 'Physical Therapy', 'Sports Medicine'
        ]
    }
    
    suggestions = []
    
    if domain and domain in skill_database:
        # Get skills for specific domain
        domain_skills = skill_database[domain]
        if search_term:
            suggestions = [skill for skill in domain_skills if search_term in skill.lower()]
        else:
            suggestions = domain_skills[:10]  # Return first 10 for domain
    elif search_term:
        # Search across all domains
        for domain_skills in skill_database.values():
            matching_skills = [skill for skill in domain_skills if search_term in skill.lower()]
            suggestions.extend(matching_skills)
        
        # Remove duplicates and limit results
        suggestions = list(set(suggestions))[:15]
    
    return JsonResponse({
        'suggestions': suggestions,
        'count': len(suggestions)
    })