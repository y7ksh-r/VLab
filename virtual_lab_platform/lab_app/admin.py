from django.contrib import admin
from .models import Subject, Experiment, Question

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
        ('Additional Information', {
            'fields': ('additional_resources',),
            'classes': ('collapse',)
        }),
    )
