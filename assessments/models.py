from django.db import models
from jobs.models import Application
from users.models import User

class MCQQuestion(models.Model):
    domain = models.CharField(max_length=100)
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=(('A','A'),('B','B'),('C','C'),('D','D')))

    def __str__(self):
        return f"{self.domain}: {self.question[:50]}"

class AssessmentResult(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='assessment')
    mcq_score = models.IntegerField(default=0, help_text="Level 1 Score")
    mcq_passed = models.BooleanField(default=False)
    
    voice_audio = models.FileField(upload_to='interviews/', null=True, blank=True)
    voice_confidence_score = models.FloatField(default=0.0, help_text="Level 2 Score")
    voice_fluency_score = models.FloatField(default=0.0)
    voice_passed = models.BooleanField(default=False)

    def __str__(self):
        return f"Assessment for {self.application}"

class HRInterview(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='hr_interview')
    hr_user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'HR'}, related_name='scheduled_interviews')
    meet_link = models.URLField(blank=True, null=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    feedback_notes = models.TextField(blank=True)
    final_status = models.CharField(max_length=20, choices=(('PENDING','Pending'), ('SELECTED','Selected'), ('REJECTED','Rejected')), default='PENDING')

    def __str__(self):
        return f"Interview with {self.hr_user.username} for {self.application}"
