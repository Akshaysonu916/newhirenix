from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('COMPANY', 'Company'),
        ('HR', 'HR'),
        ('CANDIDATE', 'Candidate'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CANDIDATE')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    def is_company(self):
        return self.role == 'COMPANY'

    def is_hr(self):
        return self.role == 'HR'

    def is_candidate(self):
        return self.role == 'CANDIDATE'


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.company_name

class HRProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hr_profile')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='hrs')

    def __str__(self):
        return f"{self.user.username} - {self.company.company_name}"

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.CharField(max_length=500, blank=True)
    experience_years = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username
