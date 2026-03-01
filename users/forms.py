from django import forms
from .models import User, CompanyProfile, CandidateProfile
from django.contrib.auth.forms import UserCreationForm

class CandidateSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    resume = forms.FileField(required=False)
    skills = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, React'}))
    experience_years = forms.IntegerField(initial=0, min_value=0)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class CompanySignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://example.com'}))
    logo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class CandidateProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    avatar = forms.ImageField(required=False)

    class Meta:
        model = CandidateProfile
        fields = ('resume', 'skills', 'experience_years')


class CompanyProfileForm(forms.ModelForm):
    email = forms.EmailField()
    avatar = forms.ImageField(required=False)

    class Meta:
        model = CompanyProfile
        fields = ('company_name', 'description', 'website', 'logo')


class HRProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar')

class HRManagementForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
