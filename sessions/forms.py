from django import forms
from django.utils import timezone
from .models import Session, Feedback

class SessionForm(forms.ModelForm):
    schedule = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Select date and time for the session'
    )
    
    class Meta:
        model = Session
        fields = [
            'title', 'description', 'thumbnail', 'category', 'skills', 
            'price', 'schedule', 'duration', 'max_participants', 'status',
            'auto_start', 'allow_late_join', 'require_approval'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, Web Development'}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'duration': forms.NumberInput(attrs={'min': '15', 'max': '480'}),
            'max_participants': forms.NumberInput(attrs={'min': '1', 'max': '50'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        
        # Set default status to 'scheduled' for new sessions
        if not self.instance.pk:  # New session
            self.fields['status'].initial = 'scheduled'
    
    def clean_schedule(self):
        schedule = self.cleaned_data['schedule']
        if schedule <= timezone.now():
            raise forms.ValidationError('Session must be scheduled for a future date and time.')
        return schedule

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none'
