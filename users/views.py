from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import User, CompanyProfile, CandidateProfile, HRProfile
from .forms import (
    CandidateSignUpForm, 
    CompanySignUpForm, 
    CandidateProfileForm, 
    CompanyProfileForm, 
    HRProfileForm,
    HRManagementForm
)

@login_required
def add_hr(request):
    if not request.user.is_company():
        messages.error(request, "Only companies can add HR accounts.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = HRManagementForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.role = 'HR'
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email')
                user.save()
                HRProfile.objects.create(
                    user=user,
                    company=request.user.company_profile
                )
                messages.success(request, f"HR account for {user.username} created successfully!")
                return redirect('hr_list')
    else:
        form = HRManagementForm()
    
    return render(request, 'users/add_hr.html', {'form': form})

@login_required
def hr_list(request):
    if not request.user.is_company():
        return redirect('dashboard')
    
    hrs = HRProfile.objects.filter(company=request.user.company_profile)
    return render(request, 'users/hr_list.html', {'hrs': hrs})

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
@transaction.atomic
def profile_edit(request):
    if request.user.role == 'CANDIDATE':
        profile = request.user.candidate_profile
        form = CandidateProfileForm(request.POST or None, request.FILES or None, instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    elif request.user.role == 'COMPANY':
        profile = request.user.company_profile
        form = CompanyProfileForm(request.POST or None, request.FILES or None, instance=profile, initial={
            'email': request.user.email,
        })
    elif request.user.role == 'HR':
        form = HRProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    else:
        messages.error(request, "Invalid role.")
        return redirect('dashboard')

    if request.method == 'POST':
        if form.is_valid():
            if request.user.role in ['CANDIDATE', 'HR']:
                request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
                request.user.last_name = form.cleaned_data.get('last_name', request.user.last_name)
            
            # Save avatar if present in form (Candidate and Company forms have it as extra field)
            if 'avatar' in form.cleaned_data and form.cleaned_data['avatar']:
                request.user.avatar = form.cleaned_data['avatar']

            request.user.email = form.cleaned_data.get('email', request.user.email)
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

    return render(request, 'users/profile_edit.html', {'form': form})

def signup_choice(request):
    return render(request, 'users/signup_choice.html')

def signup_candidate(request):
    if request.method == 'POST':
        form = CandidateSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.role = 'CANDIDATE'
                user.save()
                CandidateProfile.objects.create(
                    user=user,
                    resume=form.cleaned_data.get('resume'),
                    skills=form.cleaned_data.get('skills'),
                    experience_years=form.cleaned_data.get('experience_years')
                )
                login(request, user)
                messages.success(request, f"Welcome to Hirenix, {user.username}!")
                return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CandidateSignUpForm()
    return render(request, 'users/signup_candidate.html', {'form': form})

def signup_company(request):
    if request.method == 'POST':
        form = CompanySignUpForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.role = 'COMPANY'
                user.save()
                CompanyProfile.objects.create(
                    user=user,
                    company_name=form.cleaned_data.get('company_name'),
                    description=form.cleaned_data.get('description'),
                    website=form.cleaned_data.get('website'),
                    logo=form.cleaned_data.get('logo')
                )
                login(request, user)
                messages.success(request, "Company account created successfully!")
                return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CompanySignUpForm()
    return render(request, 'users/signup_company.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
