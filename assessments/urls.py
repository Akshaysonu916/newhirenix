from django.urls import path
from . import views

urlpatterns = [
    path('mcq/<int:application_id>/', views.take_mcq, name='take_mcq'),
    path('voice/<int:application_id>/', views.take_voice, name='take_voice'),
    path('schedule/<int:application_id>/', views.schedule_hr_interview, name='schedule_hr_interview'),
    path('feedback/<int:application_id>/', views.hr_feedback, name='hr_feedback'),
]
