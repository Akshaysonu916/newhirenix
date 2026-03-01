from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from jobs.models import Job, Application
from assessments.models import HRInterview, AssessmentResult

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    user = request.user
    context = {'role': user.role}
    
    if user.is_admin():
        context['title'] = "Admin Dashboard"
        # Admin quick stats
        context['stats'] = {
            'total_jobs': Job.objects.count(),
            'total_candidates': Application.objects.values('candidate').distinct().count(),
            'total_applications': Application.objects.count(),
        }
        return render(request, 'core/dashboards/admin.html', context)
        
    elif user.is_company():
        context['title'] = "Company Dashboard"
        if hasattr(user, 'company_profile'):
            jobs = Job.objects.filter(company=user.company_profile).annotate(
                app_count=Count('applications'),
                screened_count=Count('applications', filter=Q(applications__status__in=['LEVEL2', 'LEVEL3', 'SELECTED']))
            ).order_by('-created_at')
            context['jobs'] = jobs
        return render(request, 'core/dashboards/company.html', context)
        
    elif user.is_hr():
        context['title'] = "HR Dashboard"
        if hasattr(user, 'hr_profile'):
            # Interviews assigned to this HR
            interviews = HRInterview.objects.filter(hr_user=user).order_by('scheduled_time')
            context['interviews'] = interviews
            
            # Candidates waiting for scheduling (that passed L1 and L2 but have no interview yet)
            # Find applications in LEVEL3 but no HRInterview object yet
            pending_apps = Application.objects.filter(
                job__company=user.hr_profile.company,
                status='LEVEL3'
            ).exclude(hr_interview__isnull=False)
            context['pending_scheduling'] = pending_apps
            
        return render(request, 'core/dashboards/hr.html', context)
        
    else: # CANDIDATE
        context['title'] = "Candidate Dashboard"
        if hasattr(user, 'candidate_profile'):
            applications = Application.objects.filter(candidate=user).select_related('job', 'job__company', 'assessment').order_by('-applied_at')
            context['applications'] = applications
        return render(request, 'core/dashboards/candidate.html', context)
