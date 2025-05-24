from django.contrib import admin
from django.db import models
from .models import (
    Subject, Experiment, Question, UserProfile, LabProgress, QuestionAttempt,
    Test, MCQQuestion, TestAttempt, TestResponse
)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_at', 'updated_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('title', 'objective', 'theory')
    inlines = [QuestionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'title', 'objective')
        }),
        ('Content', {
            'fields': ('theory', 'procedure')
        }),
        ('Simulation', {
            'fields': ('simulation_url', 'simulation_embed'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {            'fields': ('additional_resources',),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'roll_no', 'role', 'branch', 'current_semester', 'division', 'is_profile_complete')
    list_filter = ('role', 'branch', 'current_semester', 'division', 'is_profile_complete')
    search_fields = ('full_name', 'roll_no', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'roll_no', 'role')
        }),
        ('Academic Details', {
            'fields': ('branch', 'current_semester', 'division')
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'profile_picture')
        }),
        ('Status', {
            'fields': ('is_profile_complete', 'created_at', 'updated_at')
        }),
    )

@admin.register(LabProgress)
class LabProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'experiment', 'status', 'last_accessed')
    list_filter = ('status', 'last_accessed')
    search_fields = ('student__username', 'student__email', 'experiment__title')
    readonly_fields = ('started_at', 'last_accessed', 'completed_at')

@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'is_correct', 'attempted_at')
    list_filter = ('is_correct', 'attempted_at')
    search_fields = ('student__username', 'student__email', 'question__question_text')

# MCQ Test Admin Classes
class MCQQuestionInline(admin.TabularInline):
    model = MCQQuestion
    extra = 3  # Start with 3 empty question forms
    fields = ('order', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks', 'explanation')
    
    def get_extra(self, request, obj=None, **kwargs):
        """Show 3 extra forms for new tests, 1 for existing tests"""
        return 3 if obj is None else 1

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'experiment', 'subject', 'difficulty', 'question_count', 'passing_score_display', 'is_active', 'created_at')
    list_filter = ('difficulty', 'is_active', 'subject', 'created_at')
    search_fields = ('title', 'description', 'subject__name', 'experiment__title')
    inlines = [MCQQuestionInline]
    readonly_fields = ('created_at', 'updated_at', 'total_marks')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Link to Experiment', {
            'fields': ('experiment', 'subject'),
            'description': 'Select an experiment to associate this test with. The subject will be auto-filled.'
        }),
        ('Test Configuration', {
            'fields': ('difficulty', 'duration', 'passing_marks', 'is_active')
        }),
        ('Auto-calculated Fields', {
            'fields': ('total_marks',),
            'classes': ('collapse',),
            'description': 'Total marks are automatically calculated based on the questions added below.'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        
        # Auto-set subject based on experiment if experiment is selected
        if obj.experiment:
            obj.subject = obj.experiment.subject
        
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Auto-calculate total marks when saving questions"""
        super().save_formset(request, form, formset, change)
        
        # Recalculate total marks if questions were modified
        if formset.model == MCQQuestion:
            test = form.instance
            total_marks = test.mcq_questions.aggregate(total=models.Sum('marks'))['total'] or 0
            if test.total_marks != total_marks:
                test.total_marks = total_marks
                test.save()
    
    def get_readonly_fields(self, request, obj=None):
        # Make created_by readonly for existing objects
        readonly = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly.append('created_by')
            # Make subject readonly if experiment is selected (auto-filled)
            if obj.experiment:
                readonly.append('subject')
        return readonly
    
    def question_count(self, obj):
        return obj.mcq_questions.count()
    question_count.short_description = 'Questions'
    
    def passing_score_display(self, obj):
        if obj.total_marks > 0:
            percentage = (obj.passing_marks / obj.total_marks) * 100
            return f"{obj.passing_marks}/{obj.total_marks} ({percentage:.1f}%)"
        return f"{obj.passing_marks}/0 (0%)"
    passing_score_display.short_description = 'Passing Score'

@admin.register(MCQQuestion)
class MCQQuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'order', 'question_text_preview', 'correct_option', 'marks')
    list_filter = ('test', 'correct_option', 'marks')
    search_fields = ('question_text', 'test__title')
    ordering = ('test', 'order')
    
    def question_text_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = 'Question Preview'

class TestResponseInline(admin.TabularInline):
    model = TestResponse
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct', 'answered_at')

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'status', 'score', 'total_marks', 'percentage', 'is_passed', 'started_at')
    list_filter = ('status', 'test', 'started_at')
    search_fields = ('student__username', 'student__email', 'test__title')
    readonly_fields = ('started_at', 'completed_at', 'percentage', 'is_passed')
    inlines = [TestResponseInline]
    
    def get_readonly_fields(self, request, obj=None):
        # Make most fields readonly for completed attempts
        readonly = list(self.readonly_fields)
        if obj and obj.status == 'completed':
            readonly.extend(['student', 'test', 'status', 'score', 'total_marks', 'time_taken'])
        return readonly

@admin.register(TestResponse)
class TestResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'selected_option', 'answered_at')
    search_fields = ('attempt__student__username', 'question__question_text')
