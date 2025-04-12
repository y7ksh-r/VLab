from django.urls import path
from . import views

app_name = 'lab_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('subject/<int:subject_id>/', views.subject_list, name='subject_list'),
    path('experiments/', views.experiment_list, name='experiment_list'),
    path('experiment/<int:experiment_id>/', views.experiment_detail, name='experiment_detail'),
] 