from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    # Conditional fields based on role
    skills = forms.CharField(max_length=500, required=False, help_text="Skills for mentors (comma-separated)")
    interests = forms.CharField(max_length=500, required=False, help_text="Interests for learners (comma-separated)")
    domain = forms.CharField(max_length=100, required=False, help_text="Primary domain/field")
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_image = forms.ImageField(required=False, help_text="Upload your profile picture")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'skills', 'interests', 'domain', 'bio', 'profile_image', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower().strip()
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def clean_skills(self):
        skills = self.cleaned_data.get('skills', '')
        if skills:
            # Clean skills for recommendation system
            skills_list = [skill.strip().title() for skill in skills.split(',') if skill.strip()]
            return ','.join(skills_list)
        return skills

    def clean_interests(self):
        interests = self.cleaned_data.get('interests', '')
        if interests:
            # Clean interests for recommendation system
            interests_list = [interest.strip().title() for interest in interests.split(',') if interest.strip()]
            return ','.join(interests_list)
        return interests

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email'].lower()
        user.role = self.cleaned_data['role']
        user.bio = self.cleaned_data.get('bio', '')
        user.skills = self.cleaned_data.get('skills', '')
        user.interests = self.cleaned_data.get('interests', '')
        user.domain = self.cleaned_data.get('domain', '')
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'skills', 'interests', 'domain', 'profile_image')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.TextInput(attrs={'placeholder': 'Enter skills separated by commas (for mentors)'}),
            'interests': forms.TextInput(attrs={'placeholder': 'Enter interests separated by commas (for learners)'}),
            'domain': forms.TextInput(attrs={'placeholder': 'Your primary domain/field'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'skills', 'interests', 'domain', 'career_goals', 'profile_image', 'location', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.TextInput(attrs={'placeholder': 'Comma-separated skills (e.g., Python, Django, Web Dev)'}),
            'interests': forms.TextInput(attrs={'placeholder': 'Comma-separated interests (e.g., AI, Machine Learning, Data Science)'}),
            'domain': forms.TextInput(attrs={'placeholder': 'Your primary learning domain (e.g., Software Engineering)'}),
            'career_goals': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your career aspirations'}),
            'location': forms.TextInput(attrs={'placeholder': 'Your location (e.g., City, Country)'}),
            'website': forms.URLInput(attrs={'placeholder': 'Your website or portfolio URL'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'})
