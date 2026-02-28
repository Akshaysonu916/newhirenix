from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import User, CompanyProfile, CandidateProfile
from .forms import CandidateSignUpForm, CompanySignUpForm

def signup_choice(request):
    return render(request, 'users/signup_choice.html')

def signup_candidate(request):
    if request.method == 'POST':
        form = CandidateSignUpForm(request.POST, request.FILES)
        if form.is_valid():
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
        form = CandidateSignUpForm()
    return render(request, 'users/signup_candidate.html', {'form': form})

def signup_company(request):
    if request.method == 'POST':
        form = CompanySignUpForm(request.POST, request.FILES)
        if form.is_valid():
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
