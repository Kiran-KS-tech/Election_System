from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Redirect base URL to the voting page
    path('', lambda r: redirect('student_vote'), name='home'),
    
    # Voting routes
    path('vote/', views.student_vote, name='student_vote'),
    path('vote/success/', views.vote_success, name='vote_success'),
    
    # Invigilator control panel routes
    path('control/', views.control_panel, name='control_panel'),
    path('control/reset/', views.reset_election, name='reset_election'),
    path('results/', views.election_results, name='election_results'),
    
    # Candidate management routes (CRUD)
    path('candidates/', views.CandidateListView.as_name() if hasattr(views.CandidateListView, 'as_name') else views.CandidateListView.as_view(), name='candidate_list'),
    path('candidates/add/', views.CandidateCreateView.as_view(), name='candidate_add'),
    path('candidates/edit/<int:pk>/', views.CandidateUpdateView.as_view(), name='candidate_edit'),
    path('candidates/delete/<int:pk>/', views.CandidateDeleteView.as_view(), name='candidate_delete'),
    
    # Authentication routes
    path('login/', auth_views.LoginView.as_view(template_name='election/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
