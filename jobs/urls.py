from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('create/', views.create_job, name='create_job'),
    path('manage/', views.company_jobs, name='company_jobs'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('<int:pk>/edit/', views.edit_job, name='edit_job'),
]
