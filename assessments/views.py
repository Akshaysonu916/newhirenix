from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HRInterview, AssessmentResult, MCQQuestion
from jobs.models import Application
from users.models import HRProfile
import random
import time

@login_required
def take_mcq(request, application_id):
    application = get_object_or_404(Application, id=application_id, candidate=request.user)
    
    if application.status != 'APPLIED' and application.status != 'LEVEL1':
        messages.info(request, "You have already completed this level or are not yet eligible.")
        return redirect('dashboard')
    
    assessment, created = AssessmentResult.objects.get_or_create(application=application)
    
    if assessment.mcq_passed:
        messages.info(request, "You have already passed the MCQ assessment.")
        return redirect('dashboard')

    domain = application.job.domain
    # Try to find existing questions for this domain
    questions = list(MCQQuestion.objects.filter(domain__icontains=domain))
    
    # If not enough questions, generate them using AI
    if len(questions) < 5:
        from .ai_utils import MCQGenerator
        generated = MCQGenerator.generate_questions(application.job.description + " " + application.job.title)
        
        for g_q in generated:
            # Avoid creating duplicates in the pool
            if not MCQQuestion.objects.filter(question=g_q['question']).exists():
                MCQQuestion.objects.create(
                    domain=domain,
                    question=g_q['question'],
                    option_a=g_q['options'][0],
                    option_b=g_q['options'][1],
                    option_c=g_q['options'][2],
                    option_d=g_q['options'][3],
                    correct_option=g_q['answer']
                )
        
        # Re-fetch the questions
        questions = list(MCQQuestion.objects.filter(domain__icontains=domain))

    # If still no questions (unlikely with 'general' fallback), use General domain
    if not questions:
        questions = list(MCQQuestion.objects.filter(domain='General'))[:5]

    if request.method == 'POST':
        # Get the IDs of the questions that were actually shown to the user
        question_ids = request.POST.getlist('question_ids')
        questions_to_grade = MCQQuestion.objects.filter(id__in=question_ids)
        
        score = 0
        total = questions_to_grade.count()
        
        for q in questions_to_grade:
            user_answer = request.POST.get(f'q_{q.id}')
            if user_answer == q.correct_option:
                score += 1
        
        final_percentage = (score / total) * 100 if total > 0 else 0
        assessment.mcq_score = int(final_percentage)
        
        if final_percentage >= 60:
            assessment.mcq_passed = True
            application.status = 'LEVEL2'
            messages.success(request, f"Congratulations! You scored {int(final_percentage)}% and passed to Level 2.")
        else:
            messages.error(request, f"You scored {int(final_percentage)}%. You need at least 60% to pass.")
            
        assessment.save()
        application.save()
        return redirect('dashboard')

    # Randomize and pick 5 for display (only for GET)
    random.shuffle(questions)
    questions = questions[:5]

    return render(request, 'assessments/mcq_quiz.html', {
        'questions': questions,
        'application': application
    })

@login_required
def take_voice(request, application_id):
    application = get_object_or_404(Application, id=application_id, candidate=request.user)
    
    if application.status != 'LEVEL2':
        messages.info(request, "You are not at the voice interview level yet.")
        return redirect('dashboard')
    
    assessment = get_object_or_404(AssessmentResult, application=application)
    
    if request.method == 'POST':
        audio_file = request.FILES.get('voice_audio')
        if audio_file:
            assessment.voice_audio = audio_file
            
            # Simple simulation of analysis
            audio_size_kb = audio_file.size / 1024
            confidence = min(audio_size_kb / 100 * 40 + random.randint(30, 50), 100)
            fluency = min(audio_size_kb / 100 * 35 + random.randint(40, 60), 100)
            
            assessment.voice_confidence_score = round(confidence, 1)
            assessment.voice_fluency_score = round(fluency, 1)
            
            if assessment.voice_confidence_score >= 60 and assessment.voice_fluency_score >= 60:
                assessment.voice_passed = True
                application.status = 'LEVEL3'
                messages.success(request, f"Voice Interview Analysis Complete. Confidence: {assessment.voice_confidence_score}%. Passed to HR Round!")
            else:
                messages.error(request, "Voice analysis complete. Score insufficient to pass.")
            
            assessment.save()
            application.save()
            return redirect('dashboard')

    return render(request, 'assessments/voice_interview.html', {
        'application': application
    })

@login_required
def schedule_hr_interview(request, application_id):
    if not request.user.is_company() and not request.user.is_hr():
        return redirect('dashboard')
    
    application = get_object_or_404(Application, id=application_id)
    # Get HR users belonging to the same company as the job
    hr_profiles = HRProfile.objects.filter(company=application.job.company)
    
    if request.method == 'POST':
        hr_id = request.POST.get('hr_user')
        scheduled_time = request.POST.get('scheduled_time')
        meet_link = request.POST.get('meet_link', 'https://meet.google.com/mock-link')
        
        if not hr_id:
            messages.error(request, "Please select an HR representative.")
            return redirect('schedule_hr_interview', application_id=application_id)

        HRInterview.objects.update_or_create(
            application=application,
            defaults={
                'hr_user_id': hr_id,
                'scheduled_time': scheduled_time,
                'meet_link': meet_link,
            }
        )
        
        application.status = 'LEVEL3' # Confirmed for HR Interview
        application.save()
        
        messages.success(request, f"HR Interview scheduled for {application.candidate.get_full_name() or application.candidate.username}.")
        return redirect('dashboard')
        
    return render(request, 'assessments/schedule_interview.html', {
        'application': application,
        'hr_profiles': hr_profiles
    })

@login_required
def hr_feedback(request, application_id):
    if not request.user.is_hr() and not request.user.is_company():
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    # If HR, ensure they are the assigned interviewer
    if request.user.is_hr():
        interview = get_object_or_404(HRInterview, application_id=application_id, hr_user=request.user)
    else:
        # Company can also see/give feedback for their jobs
        interview = get_object_or_404(HRInterview, application_id=application_id, application__job__company=request.user.company_profile)
    
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        decision = request.POST.get('decision') # SELECTED or REJECTED
        
        interview.feedback_notes = feedback
        interview.final_status = decision
        interview.save()
        
        application = interview.application
        application.status = decision
        application.save()
        
        messages.success(request, f"Interviewer decision recorded for {application.candidate.get_full_name() or application.candidate.username}.")
        return redirect('dashboard')
        
    return render(request, 'assessments/hr_feedback.html', {
        'interview': interview
    })
