from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.

class UserProfile(models.Model):
    """Extended user profile for students and admins"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    
    SEMESTER_CHOICES = [
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    ]
    
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('EEE', 'Electrical and Electronics Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('IT', 'Information Technology'),
        ('AI', 'Artificial Intelligence'),
        ('DS', 'Data Science'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    roll_no = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(r'^[A-Za-z0-9]+$', 'Only alphanumeric characters are allowed.')],
        blank=True,
        null=True
    )
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, default='CSE')
    current_semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1)
    division = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        blank=True,
        null=True
    )
    contact_number = models.CharField(
        max_length=15, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        blank=True,
        null=True
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.roll_no}) - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        # Mark profile as complete if all required fields are filled
        if self.full_name and self.roll_no and self.branch and self.current_semester and self.contact_number:
            self.is_profile_complete = True
        super().save(*args, **kwargs)

class Subject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    semester = models.IntegerField(choices=UserProfile.SEMESTER_CHOICES, default=1)
    branch = models.CharField(max_length=10, choices=UserProfile.BRANCH_CHOICES, default='CSE')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['semester', 'name']
        unique_together = ['name', 'semester', 'branch']

    def __str__(self):
        return f"{self.name} - Sem {self.semester} ({self.branch})"

class Experiment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='experiments')
    title = models.CharField(max_length=200)
    objective = models.TextField()
    theory = models.TextField()
    procedure = models.TextField()
    simulation_url = models.URLField(blank=True)
    simulation_embed = models.TextField(blank=True)
    additional_resources = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject', 'title']

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class Question(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50] + "..." if len(self.question_text) > 50 else self.question_text

class LabProgress(models.Model):
    """Track student progress in lab experiments"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_progress')
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='student_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)  # Total time spent on experiment
    notes = models.TextField(blank=True)  # Student's notes
    
    class Meta:
        unique_together = ['student', 'experiment']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.student.profile.full_name} - {self.experiment.title} ({self.status})"

class QuestionAttempt(models.Model):
    """Track student attempts at experiment questions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_attempts')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_attempts')
    answer_submitted = models.TextField()
    is_correct = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"{self.student.profile.full_name} - Q{self.question.id} - {'Correct' if self.is_correct else 'Incorrect'}"

class Test(models.Model):
    """MCQ Tests created by admin for subjects"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    experiment = models.OneToOneField(Experiment, on_delete=models.CASCADE, related_name='mcq_test', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tests')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    duration = models.IntegerField(help_text="Duration in minutes")
    total_marks = models.IntegerField(default=0)
    passing_marks = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    @property
    def question_count(self):
        return self.mcq_questions.count()

class MCQQuestion(models.Model):
    """Multiple Choice Questions for tests"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='mcq_questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    marks = models.IntegerField(default=1)
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    order = models.IntegerField(default=0, help_text="Order of question in test")
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

class TestAttempt(models.Model):
    """Track student test attempts"""
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    time_taken = models.DurationField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        # Allow multiple attempts per test per student for retakes
    
    def __str__(self):
        return f"{self.student.profile.full_name} - {self.test.title} ({self.percentage:.1f}%)"
    
    @property
    def is_passed(self):
        return self.score >= self.test.passing_marks
    
    @property
    def passed(self):
        """Alias for is_passed for template compatibility"""
        return self.is_passed

class TestResponse(models.Model):
    """Individual question responses in a test attempt"""
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(MCQQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.student.profile.full_name} - Q{self.question.order} - {self.selected_option or 'No Answer'}"
