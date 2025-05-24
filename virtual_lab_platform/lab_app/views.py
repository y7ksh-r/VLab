from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from datetime import timedelta
from .models import (
    Subject, Experiment, UserProfile, LabProgress, QuestionAttempt,
    Test, MCQQuestion, TestAttempt, TestResponse
)
from .forms import UserProfileForm, EditProfileForm

# Define locally to avoid import issues
def get_session_settings():
    """Get session settings for diagnostics"""
    return {
        'session_cookie_age': settings.SESSION_COOKIE_AGE,
        'session_expire_at_browser_close': settings.SESSION_EXPIRE_AT_BROWSER_CLOSE,
        'session_save_every_request': settings.SESSION_SAVE_EVERY_REQUEST,
    }

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff

def index(request):
    """Homepage view - shows different content based on authentication status"""
    if request.user.is_authenticated:
        return redirect('lab_app:dashboard')
    
    # For non-authenticated users, show basic info
    subjects_count = Subject.objects.filter(is_active=True).count()
    experiments_count = Experiment.objects.filter(is_active=True).count()
    
    context = {
        'subjects_count': subjects_count,
        'experiments_count': experiments_count,
    }
    return render(request, 'index.html', context)

@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    user = request.user
    
    # Check if user is admin/staff and redirect to Django admin
    if user.is_staff:
        return redirect('/admin/')
    
    # Student dashboard
    if not hasattr(user, 'profile') or not user.profile.is_profile_complete:
        return redirect('lab_app:complete_profile')
    
    profile = user.profile
    
    # Get subjects for student's semester and branch
    subjects = Subject.objects.filter(
        semester=profile.current_semester,
        branch=profile.branch,
        is_active=True
    ).annotate(
        experiment_count=Count('experiments', filter=Q(experiments__is_active=True))
    )
    
    # Get student's progress
    progress_data = LabProgress.objects.filter(student=user).select_related('experiment__subject')
    
    # Calculate progress statistics
    total_experiments = Experiment.objects.filter(
        subject__in=subjects,
        is_active=True
    ).count()
    
    completed_experiments = progress_data.filter(status='completed').count()
    in_progress_experiments = progress_data.filter(status='in_progress').count()
    
    progress_percentage = (completed_experiments / total_experiments * 100) if total_experiments > 0 else 0
    
    # Get test statistics
    available_tests = Test.objects.filter(
        subject__semester=profile.current_semester,
        subject__branch=profile.branch,
        is_active=True
    ).count()
    
    completed_tests = TestAttempt.objects.filter(
        student=user,
        status='completed'
    ).count()
    
    # Calculate average test score
    avg_test_score = TestAttempt.objects.filter(
        student=user,
        status='completed'
    ).aggregate(avg=Avg('percentage'))['avg']
    avg_test_score = round(avg_test_score, 1) if avg_test_score else 0
    
    # Recent activity
    recent_progress = progress_data.order_by('-last_accessed')[:5]
    
    # Recent test attempts
    recent_tests = TestAttempt.objects.filter(
        student=user,
        status='completed'
    ).select_related('test').order_by('-completed_at')[:3]
    
    context = {
        'profile': profile,
        'subjects': subjects,
        'total_experiments': total_experiments,
        'completed_experiments': completed_experiments,
        'in_progress_experiments': in_progress_experiments,
        'progress_percentage': round(progress_percentage, 1),
        'recent_progress': recent_progress,
        # Test statistics
        'available_tests': available_tests,
        'completed_tests': completed_tests,
        'avg_test_score': avg_test_score,
        'recent_tests': recent_tests,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

@login_required
def complete_profile(request):
    """View for completing user profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=request.user,
            branch='CSE',  # Explicitly set default values
            current_semester=1
        )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile completed successfully!')
            return redirect('lab_app:dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'account/complete_profile.html', {'form': form})

@login_required
def edit_profile(request):
    """View for editing user profile - only allows editing name and contact number"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('lab_app:dashboard')
    else:
        form = EditProfileForm(instance=profile)
    
    return render(request, 'account/edit_profile.html', {'form': form, 'profile': profile})

@login_required
def subject_list(request, subject_id):
    """View showing experiments for a specific subject"""
    subject = get_object_or_404(Subject, id=subject_id, is_active=True)
    
    # Check if student has access to this subject
    if (hasattr(request.user, 'profile') and 
        request.user.profile.role == 'student' and
        (subject.semester != request.user.profile.current_semester or
         subject.branch != request.user.profile.branch)):
        messages.error(request, 'You do not have access to this subject.')
        return redirect('lab_app:dashboard')
    
    experiments = subject.experiments.filter(is_active=True)
    
    # Get student's progress for each experiment
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        progress_dict = {}
        for progress in LabProgress.objects.filter(student=request.user, experiment__in=experiments):
            progress_dict[progress.experiment.id] = progress.status
        
        for experiment in experiments:
            experiment.progress_status = progress_dict.get(experiment.id, 'not_started')
    
    context = {
        'subject': subject,
        'experiments': experiments,
    }
    return render(request, 'subject_list.html', context)

@login_required
def experiment_detail(request, experiment_id):
    """View showing detailed experiment information"""
    experiment = get_object_or_404(Experiment, id=experiment_id, is_active=True)
    
    # Check if student has access to this experiment
    if (hasattr(request.user, 'profile') and 
        request.user.profile.role == 'student' and
        (experiment.subject.semester != request.user.profile.current_semester or
         experiment.subject.branch != request.user.profile.branch)):
        messages.error(request, 'You do not have access to this experiment.')
        return redirect('lab_app:dashboard')
    
    # Track student's progress
    progress = None
    test_attempt = None
    if hasattr(request.user, 'profile') and request.user.profile.role == 'student':
        progress, created = LabProgress.objects.get_or_create(
            student=request.user,
            experiment=experiment,
            defaults={'status': 'in_progress'}
        )
        if not created:
            progress.last_accessed = timezone.now()
            if progress.status == 'not_started':
                progress.status = 'in_progress'
            progress.save()
        
        # Check if experiment has a test and get attempt status
        if hasattr(experiment, 'mcq_test') and experiment.mcq_test:
            # Get the most recent completed attempt
            test_attempt = TestAttempt.objects.filter(
                student=request.user,
                test=experiment.mcq_test,
                status='completed'
            ).order_by('-completed_at').first()
    
    context = {
        'experiment': experiment,
        'progress': progress,
        'test_attempt': test_attempt,
        'has_test': hasattr(experiment, 'mcq_test') and experiment.mcq_test is not None,
    }
    return render(request, 'experiment_detail.html', context)

@login_required
def mark_experiment_complete(request, experiment_id):
    """Mark experiment as completed"""
    if request.method == 'POST' and hasattr(request.user, 'profile'):
        experiment = get_object_or_404(Experiment, id=experiment_id)
        
        progress, created = LabProgress.objects.get_or_create(
            student=request.user,
            experiment=experiment,
            defaults={'status': 'completed', 'completed_at': timezone.now()}
        )
        
        if not created:
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def auth_status(request):
    """View for checking authentication and session status"""
    user = request.user
    
    # Get session info
    session_info = {
        'session_key': request.session.session_key,
        'settings': get_session_settings(),
    }
    
    if '_session_init_timestamp_' in request.session:
        init_time = timezone.datetime.fromtimestamp(request.session['_session_init_timestamp_'])
        session_info['session_started'] = init_time
    
    if '_last_activity_' in request.session:
        last_activity = timezone.datetime.fromtimestamp(request.session['_last_activity_'])
        session_info['last_activity'] = last_activity
    
    # Get user info
    user_info = {
        'username': user.username,
        'email': user.email,
        'is_authenticated': user.is_authenticated,
        'last_login': user.last_login,
        'date_joined': user.date_joined,
    }
    
    # Get profile info
    try:
        profile = user.profile
        profile_info = {
            'role': profile.get_role_display(),
            'full_name': profile.full_name,
            'college_id': profile.college_id,
            'branch': profile.get_branch_display(),
            'current_semester': profile.get_current_semester_display(),
            'is_profile_complete': profile.is_profile_complete,
        }
    except UserProfile.DoesNotExist:
        profile_info = {'error': 'No profile exists for this user.'}
    
    context = {
        'user_info': user_info,
        'profile_info': profile_info,
        'session_info': session_info,
    }
    
    return render(request, 'account/auth_status.html', context)

def about(request):
    """About page view"""
    return render(request, 'about.html')

def contact(request):
    """Contact page view"""
    return render(request, 'contact.html')

# MCQ Test Views (Integrated with Experiments)
@login_required
def experiment_test(request, experiment_id):
    """View for taking the experiment test"""
    experiment = get_object_or_404(Experiment, id=experiment_id, is_active=True)
    
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('lab_app:dashboard')
    
    # Check if experiment has a test
    if not hasattr(experiment, 'mcq_test') or not experiment.mcq_test:
        messages.error(request, 'This experiment does not have a test.')
        return redirect('lab_app:experiment_detail', experiment_id=experiment.id)
    
    test = experiment.mcq_test
    profile = request.user.profile
    
    # Check access
    if (experiment.subject.semester != profile.current_semester or 
        experiment.subject.branch != profile.branch):
        messages.error(request, 'You do not have access to this experiment.')
        return redirect('lab_app:dashboard')
    
    # Handle retakes - check for existing attempts
    existing_started = TestAttempt.objects.filter(
        student=request.user,
        test=test,
        status='started'
    ).first()
    
    if existing_started:
        # Use the existing started attempt
        attempt = existing_started
    else:
        # Create a new attempt (either first attempt or retake)
        attempt = TestAttempt.objects.create(
            student=request.user,
            test=test,
            status='started',
            total_marks=test.total_marks,
        )
    
    # Handle test submission
    if request.method == 'POST':
        return handle_experiment_test_submission(request, experiment, test, attempt)
    
    # Get test questions
    questions = test.mcq_questions.all().order_by('order')
    
    # Get existing responses
    responses = TestResponse.objects.filter(attempt=attempt)
    response_dict = {r.question.id: r.selected_option for r in responses}
    
    # Add existing answers to questions
    for question in questions:
        question.selected_answer = response_dict.get(question.id, '')
    
    context = {
        'experiment': experiment,
        'test': test,
        'attempt': attempt,
        'questions': questions,
        'profile': profile,
    }
    return render(request, 'experiment_test.html', context)

def handle_experiment_test_submission(request, experiment, test, attempt):
    """Handle experiment test answer submission"""
    if attempt.status == 'completed':
        messages.error(request, 'This test has already been completed.')
        return redirect('lab_app:experiment_test_result', experiment_id=experiment.id)
    
    # Process each question
    questions = test.mcq_questions.all()
    total_score = 0
    
    for question in questions:
        selected_option = request.POST.get(f'question_{question.id}')
        
        if selected_option:
            is_correct = selected_option == question.correct_option
            if is_correct:
                total_score += question.marks
            
            # Update or create response
            response, created = TestResponse.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'selected_option': selected_option,
                    'is_correct': is_correct,
                }
            )
    
    # Update attempt
    attempt.status = 'completed'
    attempt.score = total_score
    attempt.percentage = (total_score / test.total_marks * 100) if test.total_marks > 0 else 0
    attempt.completed_at = timezone.now()
    attempt.time_taken = attempt.completed_at - attempt.started_at
    attempt.save()
    
    # Check if test passed and mark experiment as completed
    if attempt.is_passed:
        # Mark experiment as completed
        progress, created = LabProgress.objects.get_or_create(
            student=request.user,
            experiment=experiment,
            defaults={'status': 'completed', 'completed_at': timezone.now()}
        )
        
        if not created:
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.save()
        
        messages.success(request, f'Congratulations! You passed the test with {attempt.percentage:.1f}% and completed the experiment!')
    else:
        messages.warning(request, f'You scored {total_score}/{test.total_marks} ({attempt.percentage:.1f}%). You need {test.passing_marks} marks to pass and complete the experiment.')
    
    return redirect('lab_app:experiment_test_result', experiment_id=experiment.id)

@login_required
def experiment_test_result(request, experiment_id):
    """View showing experiment test results"""
    experiment = get_object_or_404(Experiment, id=experiment_id)
    
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('lab_app:dashboard')
    
    if not hasattr(experiment, 'mcq_test') or not experiment.mcq_test:
        messages.error(request, 'This experiment does not have a test.')
        return redirect('lab_app:experiment_detail', experiment_id=experiment.id)
    
    test = experiment.mcq_test
    
    # Get the most recent completed attempt
    attempt = TestAttempt.objects.filter(
        student=request.user, 
        test=test,
        status='completed'
    ).order_by('-completed_at').first()
    
    if not attempt:
        messages.error(request, 'You have not completed this test yet.')
        return redirect('lab_app:experiment_detail', experiment_id=experiment.id)
    
    if attempt.status != 'completed':
        messages.error(request, 'Test not completed yet.')
        return redirect('lab_app:experiment_test', experiment_id=experiment.id)
    
    # Get detailed responses
    responses = TestResponse.objects.filter(attempt=attempt).select_related('question').order_by('question__order')
    
    # Calculate statistics
    total_questions = responses.count()
    correct_answers = responses.filter(is_correct=True).count()
    incorrect_answers = total_questions - correct_answers
    
    # Get experiment progress
    try:
        progress = LabProgress.objects.get(student=request.user, experiment=experiment)
    except LabProgress.DoesNotExist:
        progress = None
    
    context = {
        'experiment': experiment,
        'test': test,
        'test_attempt': attempt,  # Fixed variable name for template
        'attempt': attempt,  # Keep for backwards compatibility
        'test_responses': responses,  # Fixed variable name for template
        'responses': responses,  # Keep for backwards compatibility
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'progress': progress,
        'profile': request.user.profile,
    }
    return render(request, 'experiment_test_result.html', context)

@login_required
def student_progress(request):
    """View showing student's overall progress and test insights"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('lab_app:dashboard')
    
    profile = request.user.profile
    
    # Get all test attempts
    attempts = TestAttempt.objects.filter(
        student=request.user,
        status='completed'
    ).select_related('test__subject').order_by('-completed_at')
    
    # Calculate average score
    if attempts:
        avg_score = attempts.aggregate(avg=Avg('percentage'))['avg']
        avg_score = round(avg_score, 1) if avg_score else 0
    else:
        avg_score = 0
    
    # Group attempts by subject
    subject_stats = {}
    for attempt in attempts:
        subject_name = attempt.test.subject.name
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {
                'attempts': [],
                'total_score': 0,
                'total_tests': 0,
                'avg_score': 0
            }
        
        subject_stats[subject_name]['attempts'].append(attempt)
        subject_stats[subject_name]['total_score'] += attempt.percentage
        subject_stats[subject_name]['total_tests'] += 1
    
    # Calculate average for each subject
    for subject_name, stats in subject_stats.items():
        stats['avg_score'] = round(stats['total_score'] / stats['total_tests'], 1)
    
    # Get experiment progress
    experiment_progress = LabProgress.objects.filter(student=request.user).select_related('experiment__subject')
    total_experiments = experiment_progress.count()
    completed_experiments = experiment_progress.filter(status='completed').count()
    
    experiment_completion_rate = (completed_experiments / total_experiments * 100) if total_experiments > 0 else 0
    
    context = {
        'profile': profile,
        'attempts': attempts[:10],  # Recent 10 attempts
        'avg_score': avg_score,
        'subject_stats': subject_stats,
        'total_experiments': total_experiments,
        'completed_experiments': completed_experiments,
        'experiment_completion_rate': round(experiment_completion_rate, 1),
        'total_test_attempts': attempts.count(),
    }
    return render(request, 'tests/student_progress.html', context)
