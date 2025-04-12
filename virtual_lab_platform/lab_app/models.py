from django.db import models

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Experiment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='experiments')
    title = models.CharField(max_length=200)
    objective = models.TextField()
    theory = models.TextField()
    procedure = models.TextField(blank=True)
    simulation_url = models.URLField(blank=True)
    simulation_embed = models.TextField(blank=True)
    additional_resources = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class Question(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question for {self.experiment.title}"
