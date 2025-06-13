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
        widget=forms.SelectMultiple,
        label='Training Days',
        required=True
    )

    is_expert = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput()
    )

    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}),
        required=False,  # Możesz ustawić na True, jeśli notatki są obowiązkowe
        label='Notatki',
    )

    class Meta:
        model = TrainingPlan
        fields = ['name', 'exercises', 'intensity', 'training_days', 'notes', 'is_expert']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pobranie użytkownika
        super().__init__(*args, **kwargs)
        if user:
            self.instance.user = user  # Przypisanie user_id


class TrainingPlanNotesForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ['notes', 'send_notification']


class TrainingPlanTrainerNotesForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ['trainer_notes', 'send_notification']
