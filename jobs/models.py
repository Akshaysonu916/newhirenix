from django.db import models
from users.models import CompanyProfile, User

class Job(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    domain = models.CharField(max_length=100)  # e.g., Python, Frontend, Sales
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    location = models.CharField(max_length=100)
    salary_range = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

class Application(models.Model):
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('LEVEL1', 'Level 1: MCQ Pending'),
        ('LEVEL2', 'Level 2: Voice Pending'),
        ('LEVEL3', 'Level 3: HR Pending'),
        ('SELECTED', 'Selected'),
        ('REJECTED', 'Rejected')
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', limit_choices_to={'role': 'CANDIDATE'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    ats_score = models.IntegerField(default=0)  # Parsed ATS filtering score on resume
    resume_text = models.TextField(blank=True, null=True) # Extracted context
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.job.title}"
