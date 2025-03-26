# forms.py
from django import forms
from .models import TrainingPlan, Exercise

class TrainingPlanForm(forms.ModelForm):
    exercises = forms.ModelMultipleChoiceField(
        queryset=Exercise.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Możesz użyć też SelectMultiple
        required=True
    )

    class Meta:
        model = TrainingPlan
        fields = ['name', 'exercises']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pobranie użytkownika
        super().__init__(*args, **kwargs)
        if user:
            self.instance.user = user  # Przypisanie user_id
