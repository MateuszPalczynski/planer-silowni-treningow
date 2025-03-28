from django.db import models
from django.contrib.auth.models import User

class Exercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class TrainingPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Powiązanie z użytkownikiem
    name = models.CharField(max_length=255)  # Nazwa planu treningowego
    exercises = models.ManyToManyField(Exercise)
    
   def __str__(self):
        return f'{self.name} (użytkownik: {self.user.username})'
