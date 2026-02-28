from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
        return render(request, 'core/dashboards/admin.html', context)
    elif user.is_company():
        context['title'] = "Company Dashboard"
        return render(request, 'core/dashboards/company.html', context)
    elif user.is_hr():
        context['title'] = "HR Dashboard"
        return render(request, 'core/dashboards/hr.html', context)
    else: # CANDIDATE
        context['title'] = "Candidate Dashboard"
        return render(request, 'core/dashboards/candidate.html', context)
