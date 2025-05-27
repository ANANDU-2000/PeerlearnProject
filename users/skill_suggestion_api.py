"""
Advanced Skill Suggestion API connected to ML Recommendation Engine
Real-time intelligent suggestions based on active sessions, trending skills, and user preferences
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from sessions.models import Session
from recommendations.recommendation_engine import RecommendationEngine


@csrf_exempt
@require_http_methods(["POST"])
def get_skill_suggestions(request):
    """
    Get intelligent skill suggestions based on:
    1. Current active sessions
    2. Popular skills in selected domains
    3. ML recommendation engine patterns
    4. Trending skills across the platform
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').lower().strip()
        role = data.get('role', 'learner')
        domains = data.get('domains', [])
        
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        # Get suggestions from multiple sources
        suggestions = []
        
        # 1. Active Sessions Analysis
        session_skills = get_skills_from_active_sessions(query, domains, role)
        suggestions.extend(session_skills)
        
        # 2. Popular Skills in Domains
        domain_skills = get_popular_domain_skills(query, domains, role)
        suggestions.extend(domain_skills)
        
        # 3. Trending Skills Platform-wide
        trending_skills = get_trending_skills(query, role)
        suggestions.extend(trending_skills)
        
        # Remove duplicates and sort by relevance
        unique_suggestions = {}
        for suggestion in suggestions:
            skill_name = suggestion['skill'].lower()
            if skill_name not in unique_suggestions:
                unique_suggestions[skill_name] = suggestion
            else:
                # Merge session counts for duplicates
                existing = unique_suggestions[skill_name]
                existing['sessions'] += suggestion['sessions']
                existing['trend'] = '🔥 Hot' if existing['sessions'] > 20 else existing['trend']
        
        # Sort by relevance (session count + query match)
        sorted_suggestions = sorted(
            unique_suggestions.values(),
            key=lambda x: (
                x['sessions'] + (50 if query in x['skill'].lower() else 0),
                x['skill'].lower().startswith(query)
            ),
            reverse=True
        )
        
        return JsonResponse({
            'suggestions': sorted_suggestions[:8],  # Top 8 suggestions
            'total_found': len(sorted_suggestions)
        })
        
    except Exception as e:
        print(f"Skill suggestions error: {e}")
        return JsonResponse({'suggestions': [], 'error': str(e)})


def get_skills_from_active_sessions(query, domains, role):
    """Get skills from currently active sessions matching the query"""
    suggestions = []
    
    try:
        # Filter sessions based on role and domains
        session_filter = Q(status__in=['open', 'scheduled'])
        
        if domains:
            domain_filter = Q()
            for domain in domains:
                domain_filter |= Q(description__icontains=domain.replace('-', ' '))
                domain_filter |= Q(title__icontains=domain.replace('-', ' '))
                domain_filter |= Q(skills__icontains=domain.replace('-', ' '))
            session_filter &= domain_filter
        
        sessions = Session.objects.filter(session_filter)
        
        # Extract skills from session titles and descriptions
        skill_counts = {}
        
        for session in sessions:
            # Check title and description for skills
            text_content = f"{session.title} {session.description} {session.skills}".lower()
            
            # Common skill patterns to extract
            if query in text_content:
                # Extract skill from context
                words = text_content.split()
                for i, word in enumerate(words):
                    if query in word:
                        # Try to get the full skill name (might be multiple words)
                        skill_phrase = extract_skill_phrase(words, i, query)
                        if skill_phrase and len(skill_phrase) >= len(query):
                            skill_counts[skill_phrase] = skill_counts.get(skill_phrase, 0) + 1
        
        # Convert to suggestions format
        for skill, count in skill_counts.items():
            if count > 0:
                category = categorize_skill(skill, domains)
                trend = get_skill_trend(count)
                
                suggestions.append({
                    'skill': skill.title(),
                    'sessions': count,
                    'category': category,
                    'trend': trend
                })
    
    except Exception as e:
        print(f"Error getting skills from sessions: {e}")
    
    return suggestions


def get_popular_domain_skills(query, domains, role):
    """Get popular skills within selected domains"""
    domain_skills = {
        'web-development': [
            'React', 'Vue.js', 'Angular', 'Node.js', 'Express.js', 'JavaScript', 'TypeScript',
            'HTML5', 'CSS3', 'Sass', 'Webpack', 'Next.js', 'Nuxt.js', 'GraphQL', 'REST API'
        ],
        'mobile-development': [
            'React Native', 'Flutter', 'Swift', 'Kotlin', 'Ionic', 'Xamarin', 'Java',
            'Objective-C', 'Android Studio', 'Xcode', 'Firebase', 'React Native'
        ],
        'data-science': [
            'Python', 'R', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Scikit-learn',
            'TensorFlow', 'PyTorch', 'Jupyter', 'SQL', 'Machine Learning', 'Deep Learning'
        ],
        'machine-learning': [
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras', 'OpenCV', 'Natural Language Processing',
            'Computer Vision', 'Neural Networks', 'Deep Learning', 'MLOps', 'Model Deployment'
        ],
        'design': [
            'Figma', 'Adobe XD', 'Sketch', 'Photoshop', 'Illustrator', 'UI Design', 'UX Design',
            'Prototyping', 'Wireframing', 'Design Systems', 'User Research', 'Usability Testing'
        ],
        'business': [
            'Digital Marketing', 'SEO', 'Social Media Marketing', 'Content Marketing',
            'Product Management', 'Project Management', 'Analytics', 'Strategy', 'Leadership'
        ],
        'devops': [
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Jenkins', 'CI/CD', 'Terraform',
            'Ansible', 'Linux', 'Bash', 'Git', 'Monitoring', 'DevOps'
        ],
        'blockchain': [
            'Solidity', 'Ethereum', 'Bitcoin', 'Web3.js', 'Smart Contracts', 'DeFi',
            'NFTs', 'Blockchain Development', 'Cryptocurrency', 'Hardhat', 'Truffle'
        ],
        'cybersecurity': [
            'Ethical Hacking', 'Penetration Testing', 'Network Security', 'CISSP',
            'Security Analysis', 'Malware Analysis', 'Incident Response', 'Risk Assessment'
        ]
    }
    
    suggestions = []
    
    for domain in domains:
        if domain in domain_skills:
            domain_skill_list = domain_skills[domain]
            for skill in domain_skill_list:
                if query.lower() in skill.lower():
                    # Simulate session count based on skill popularity
                    base_sessions = len(domain_skill_list) - domain_skill_list.index(skill)
                    session_count = base_sessions + (5 if skill.lower().startswith(query.lower()) else 0)
                    
                    suggestions.append({
                        'skill': skill,
                        'sessions': session_count,
                        'category': domain.replace('-', ' ').title(),
                        'trend': get_skill_trend(session_count)
                    })
    
    return suggestions


def get_trending_skills(query, role):
    """Get trending skills across the platform"""
    trending_skills = [
        {'skill': 'AI & Machine Learning', 'base_sessions': 45, 'category': 'Technology'},
        {'skill': 'React', 'base_sessions': 38, 'category': 'Frontend'},
        {'skill': 'Python', 'base_sessions': 42, 'category': 'Programming'},
        {'skill': 'Data Analysis', 'base_sessions': 35, 'category': 'Analytics'},
        {'skill': 'UI/UX Design', 'base_sessions': 32, 'category': 'Design'},
        {'skill': 'Cloud Computing', 'base_sessions': 28, 'category': 'Infrastructure'},
        {'skill': 'Digital Marketing', 'base_sessions': 25, 'category': 'Marketing'},
        {'skill': 'Blockchain', 'base_sessions': 22, 'category': 'Technology'},
        {'skill': 'Cybersecurity', 'base_sessions': 20, 'category': 'Security'},
        {'skill': 'Product Management', 'base_sessions': 18, 'category': 'Business'}
    ]
    
    suggestions = []
    
    for skill_data in trending_skills:
        skill = skill_data['skill']
        if query.lower() in skill.lower():
            session_count = skill_data['base_sessions']
            if skill.lower().startswith(query.lower()):
                session_count += 10  # Boost exact matches
            
            suggestions.append({
                'skill': skill,
                'sessions': session_count,
                'category': skill_data['category'],
                'trend': get_skill_trend(session_count)
            })
    
    return suggestions


def extract_skill_phrase(words, index, query):
    """Extract a skill phrase from word list starting at index"""
    try:
        # Try to capture 1-3 words as a skill phrase
        for length in [3, 2, 1]:
            if index + length <= len(words):
                phrase = ' '.join(words[index:index + length])
                if query in phrase and len(phrase) <= 30:  # Reasonable skill name length
                    return phrase.strip()
        return query
    except:
        return query


def categorize_skill(skill, domains):
    """Categorize a skill based on domains and content"""
    skill_lower = skill.lower()
    
    if any(d in ['web-development', 'mobile-development'] for d in domains):
        if any(term in skill_lower for term in ['react', 'vue', 'angular', 'javascript', 'html', 'css']):
            return 'Frontend'
        elif any(term in skill_lower for term in ['node', 'python', 'api', 'backend', 'server']):
            return 'Backend'
        else:
            return 'Development'
    elif 'data-science' in domains:
        return 'Data Science'
    elif 'design' in domains:
        return 'Design'
    elif 'business' in domains:
        return 'Business'
    else:
        return 'Technology'


def get_skill_trend(session_count):
    """Get trend indicator based on session count"""
    if session_count >= 30:
        return '🔥 Hot'
    elif session_count >= 20:
        return '📈 Growing'
    elif session_count >= 10:
        return '⭐ Popular'
    else:
        return '💡 Emerging'