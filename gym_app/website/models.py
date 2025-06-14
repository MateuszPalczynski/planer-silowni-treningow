from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Exercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TrainingPlan(models.Model):
    INTENSITY_CHOICES = [
        ('low', 'Niska'),
        ('medium', 'Średnia'),
        ('high', 'Wysoka'),
    ]

    DAYS_OF_WEEK = [
        ('mon', 'Poniedziałek'),
        ('tue', 'Wtorek'),
        ('wed', 'Środa'),
        ('thu', 'Czwartek'),
        ('fri', 'Piątek'),
        ('sat', 'Sobota'),
        ('sun', 'Niedziela'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Powiązanie z użytkownikiem
    name = models.CharField(max_length=255)  # Nazwa planu treningowego

    exercises = models.ManyToManyField(
        Exercise,
        through='TrainingPlanExercise',
        related_name='plans'
    )

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
        days = ', '.join([dict(self.DAYS_OF_WEEK).get(day, day) for day in self.training_days]) if self.training_days else 'Brak dni'
        return f'{self.name} - {self.get_intensity_display()}, Dni treningowe: {days}'

    def get_training_days_display(self):
        day_map = dict(self.DAYS_OF_WEEK)
        return [day_map.get(day, day) for day in self.training_days]


class TrainingPlanExercise(models.Model):
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    repetitions = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('training_plan', 'exercise')

    def __str__(self):
        return f"{self.training_plan.name} – {self.exercise.name}: {self.repetitions} reps"

class ActivityLog(models.Model):
    """Model do zapisywania logów aktywności użytkowników."""
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Użytkownik"
    )
    action = models.TextField(verbose_name="Aktywność")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Znacznik czasu")

    class Meta:
        verbose_name = "Log Aktywności"
        verbose_name_plural = "Logi Aktywności"
        ordering = ['-timestamp'] # Najnowsze na górze

    def __str__(self):
        return f'{self.timestamp.strftime("%Y-%m-%d %H:%M:%S")} - {self.user.username if self.user else "System"} - {self.action}'

class TrainingPlanCompletion(models.Model):
    training_plan = models.ForeignKey('TrainingPlan', on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_completed = models.DateField()

    class Meta:
        unique_together = ('training_plan', 'user', 'date_completed')
        ordering = ['-date_completed']

    def __str__(self):
        return f"{self.user} completed {self.training_plan} on {self.date_completed}"