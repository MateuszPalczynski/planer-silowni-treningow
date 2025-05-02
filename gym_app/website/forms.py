# forms.py
from django import forms
from .models import TrainingPlan, Exercise

class TrainingPlanForm(forms.ModelForm):
    exercises = forms.ModelMultipleChoiceField(
        queryset=Exercise.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Możesz użyć też SelectMultiple
        required=True
    )

    intensity = forms.ChoiceField(
        choices=TrainingPlan.INTENSITY_CHOICES,
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Level of Intensity'
    )
    
    training_days = forms.MultipleChoiceField(
        choices=TrainingPlan.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        label='Training Days',
        required=True
    )

    class Meta:
        model = TrainingPlan
        fields = ['name', 'exercises', 'intensity', 'training_days']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pobranie użytkownika
        super().__init__(*args, **kwargs)
        if user:
            self.instance.user = user  # Przypisanie user_id
