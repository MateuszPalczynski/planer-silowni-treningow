from django.contrib import admin
from .models import Exercise, TrainingPlan, TrainingPlanExercise

class TrainingPlanExerciseInline(admin.TabularInline):
    model = TrainingPlanExercise
    extra = 1

class TrainingPlanAdmin(admin.ModelAdmin):
    inlines = [TrainingPlanExerciseInline]

admin.site.register(Exercise)
admin.site.register(TrainingPlan, TrainingPlanAdmin)
