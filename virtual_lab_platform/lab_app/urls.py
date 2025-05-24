from django.urls import path
from . import views

app_name = 'lab_app'

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/complete/', views.complete_profile, name='complete_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Lab content
    path('subject/<int:subject_id>/', views.subject_list, name='subject_list'),
    path('experiment/<int:experiment_id>/', views.experiment_detail, name='experiment_detail'),
    path('experiment/<int:experiment_id>/complete/', views.mark_experiment_complete, name='mark_experiment_complete'),
    path('experiment/<int:experiment_id>/test/', views.experiment_test, name='experiment_test'),
    path('experiment/<int:experiment_id>/test/result/', views.experiment_test_result, name='experiment_test_result'),
    
    # Student Progress
    path('progress/', views.student_progress, name='student_progress'),
    
    # Authentication status
    path('auth/status/', views.auth_status, name='auth_status'),
]