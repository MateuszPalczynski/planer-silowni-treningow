from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TrainingPlan(models.Model):
    INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    DAYS_OF_WEEK = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Powiązanie z użytkownikiem
    name = models.CharField(max_length=255)  # Nazwa planu treningowego
    exercises = models.ManyToManyField(Exercise)
    intensity = models.CharField(
        max_length=6,
        choices=INTENSITY_CHOICES,
        default='medium',
    )
    training_days = models.JSONField(default=list)
    notes = models.TextField(null=True, blank=True)
    send_notification = models.BooleanField(default=False, help_text="Wysyłaj powiadomienia e-mail w dni treningowe")
    trainer_notes = models.TextField(null=True, blank=True)
    is_expert = models.BooleanField(default=False)

    def __str__(self):
        days = ', '.join(self.training_days).title() if self.training_days else 'No days set'
        return f'{self.name} - {self.get_intensity_display()} Intensity, Training Days: {days}'
    
    def get_training_days_display(self):
        day_map = dict(self.DAYS_OF_WEEK)
        return [day_map.get(day, day) for day in self.training_days]

