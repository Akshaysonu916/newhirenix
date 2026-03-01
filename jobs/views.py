from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Job, Application
from .forms import JobForm
from users.models import CompanyProfile

@login_required
def create_job(request):
    if not request.user.is_company():
        messages.error(request, "Only companies can post jobs.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user.company_profile
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('company_jobs')
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Post a New Job'})

@login_required
def edit_job(request, pk):
    if not request.user.is_company():
        messages.error(request, "Only companies can edit jobs.")
        return redirect('dashboard')
    
    job = get_object_or_404(Job, pk=pk, company=request.user.company_profile)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('company_jobs')
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/job_form.html', {'form': form, 'title': f'Edit Job: {job.title}', 'edit_mode': True})

@login_required
def company_jobs(request):
    if not request.user.is_company():
        return redirect('dashboard')
    
    jobs = Job.objects.filter(company=request.user.company_profile).annotate(
        total_apps=Count('applications')
    ).order_by('-created_at')
    return render(request, 'jobs/company_jobs.html', {'jobs': jobs})

@login_required
def job_applicants(request, job_id):
    if not request.user.is_company():
        return redirect('dashboard')
    
    job = get_object_or_404(Job, id=job_id, company=request.user.company_profile)
    applications = Application.objects.filter(job=job).select_related('candidate').order_by('-ats_score')
    
    return render(request, 'jobs/job_applicants.html', {'job': job, 'applications': applications})

def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    if request.user.is_authenticated and request.user.is_candidate():
        has_applied = Application.objects.filter(job=job, candidate=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def apply_job(request, job_id):
    if not request.user.is_candidate():
        messages.error(request, "Only candidates can apply for jobs.")
        return redirect('job_list')
    
    job = get_object_or_404(Job, id=job_id)
    
    # Check if already applied
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        # Create application
        application = Application.objects.create(
            job=job,
            candidate=request.user,
            status='APPLIED'
        )
        
        # Extract skills/text from resume for ATS simulation
        if hasattr(request.user, 'candidate_profile') and request.user.candidate_profile.resume:
            # Simulation of ATS scoring based on basic factors
            application.ats_score = random.randint(40, 95)
            application.save()
            
        messages.success(request, f"Successfully applied for {job.title}!")
        return redirect('dashboard')
        
    return redirect('job_detail', pk=job_id)

import random
