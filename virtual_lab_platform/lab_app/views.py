from django.shortcuts import render, get_object_or_404
from .models import Subject, Experiment

def index(request):
    subjects = Subject.objects.all()
    return render(request, 'index.html', {'subjects': subjects})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def subject_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    experiments = subject.experiments.all()
    return render(request, 'subject_list.html', {
        'subject': subject,
        'experiments': experiments
    })

def experiment_list(request):
    experiments = Experiment.objects.all()
    return render(request, 'experiment_list.html', {'experiments': experiments})

def experiment_detail(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    return render(request, 'experiment_detail.html', {'experiment': experiment})
