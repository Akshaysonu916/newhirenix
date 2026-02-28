from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_choice, name='signup_choice'),
    path('signup/company/', views.signup_company, name='signup_company'),
    path('signup/candidate/', views.signup_candidate, name='signup_candidate'),
]
