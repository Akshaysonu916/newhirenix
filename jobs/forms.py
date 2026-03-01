from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'domain', 'salary_range', 'location', 'description', 'responsibilities', 'requirements']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the role...'}),
            'responsibilities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List key responsibilities...'}),
            'requirements': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List requirements...'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Senior Python Developer'}),
            'domain': forms.TextInput(attrs={'placeholder': 'e.g. Backend, AI, Frontend'}),
            'salary_range': forms.TextInput(attrs={'placeholder': 'e.g. $100k - $120k'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Remote, New York, NY'}),
        }
