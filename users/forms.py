from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    skills = forms.CharField(max_length=500, required=True, help_text="Skills for recommendation system")
    expertise = forms.CharField(max_length=100, required=True, help_text="Domain expertise")
    bio = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'skills', 'expertise', 'bio', 'password1', 'password2')
    
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
        if not skills or not skills.strip():
            raise forms.ValidationError("Please add at least one skill for recommendations.")
        
        # Clean skills for ML recommendation system
        skills_list = [skill.strip().title() for skill in skills.split(',') if skill.strip()]
        if len(skills_list) == 0:
            raise forms.ValidationError("Please add at least one skill.")
        
        return ','.join(skills_list)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email'].lower()
        user.role = self.cleaned_data['role']
        user.bio = self.cleaned_data.get('bio', '')
        user.skills = self.cleaned_data.get('skills', '')
        user.expertise = self.cleaned_data.get('expertise', '')
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
        fields = ('first_name', 'last_name', 'email', 'bio', 'expertise', 'profile_image')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'expertise': forms.TextInput(attrs={'placeholder': 'Enter skills separated by commas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
