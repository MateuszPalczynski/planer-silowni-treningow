from django.contrib import admin
from .models import Exercise, TrainingPlan, TrainingPlanExercise, ActivityLog

admin.site.register(Exercise)
admin.site.register(TrainingPlan)
admin.site.register(TrainingPlanExercise)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')
    list_filter = ('user', 'timestamp')
    search_fields = ('user__username', 'action')
    readonly_fields = ('timestamp', 'user', 'action') # Logi powinny być tylko do odczytu

    def has_add_permission(self, request):
        return False # Nikt nie może dodawać logów ręcznie

    def has_change_permission(self, request, obj=None):
        return False # Nikt nie może edytować logów

    def has_delete_permission(self, request, obj=None):
        return False # Nikt nie może usuwać logów