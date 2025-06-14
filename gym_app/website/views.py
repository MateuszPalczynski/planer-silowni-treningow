# website/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import json
from django.utils.dateparse import parse_date
from .models import TrainingPlanCompletion

from .forms import TrainingPlanForm, TrainingPlanNotesForm, TrainingPlanTrainerNotesForm
from .models import TrainingPlan, TrainingPlanExercise, Exercise, TrainingPlanCompletion


def home(request):
    """
    Wyświetla stronę główną (home.html) z listą planów i popupem do tworzenia nowego planu.
    """
    form = TrainingPlanForm()
    training_plans = []
    expert_plans = []
    user = request.user
    is_trainer = False

    if user.is_authenticated:
        is_trainer = user.groups.filter(name='trener').exists()
        training_plans = (
            TrainingPlan.objects.filter(is_expert=False)  # Trener widzi wszystkie plany podopiecznych
            if is_trainer
            else TrainingPlan.objects.filter(user=user, is_expert=False)  # Użytkownik widzi tylko swoje
        )
        # Plany eksperckie są dostępne dla wszystkich zalogowanych
        expert_plans = TrainingPlan.objects.filter(is_expert=True)

    # Pobieramy WSZYSTKIE ćwiczenia, by wyświetlić je w popupie
    all_exercises = Exercise.objects.all().order_by('name')

    # Przygotowanie danych JSON dla JavaScript
    training_plans_json = []
    if user.is_authenticated:
        for plan in training_plans:
            plan_data = {
                'id': plan.id,
                'name': plan.name,
                'intensity': plan.intensity,
                'training_days': plan.training_days,
                'exercises': []
            }
            for tpe in plan.trainingplanexercise_set.all():
                plan_data['exercises'].append({
                    'id': tpe.exercise.id,
                    'name': tpe.exercise.name,
                    'repetitions': tpe.repetitions
                })
            training_plans_json.append(plan_data)

    return render(request, 'home.html', {
        'form': form,
        'training_plans': training_plans,
        'expert_plans': expert_plans,
        'is_trainer': is_trainer,
        'all_exercises': all_exercises,
        'training_plans_json': json.dumps(training_plans_json),
    })


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatyczne logowanie po rejestracji
            messages.success(request, f'Konto zostało utworzone! Jesteś teraz zalogowany.')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def create_training_plan(request):
    """
    Widok do obsługi POST z formularza w popupie (home.html).
    Zapisuje nowy TrainingPlan. Obsługuje dwa przypadki:
    1. Kopiowanie planu eksperckiego (jeśli przekazano 'plan_id').
    2. Tworzenie nowego planu od zera.
    """
    if request.method == 'POST':
        expert_plan_id = request.POST.get('plan_id')

        # Przypadek 1: Użytkownik wybrał gotowy plan ekspercki
        if expert_plan_id:
            original_plan = get_object_or_404(TrainingPlan, id=expert_plan_id, is_expert=True)

            # Stwórz nową instancję dla zalogowanego użytkownika, kopiując dane
            new_plan = TrainingPlan.objects.create(
                user=request.user,
                name=original_plan.name,
                intensity=original_plan.intensity,
                training_days=original_plan.training_days,
                is_expert=False,  # Nowy plan nie jest już szablonem eksperckim
                trainer_notes=original_plan.trainer_notes
            )
            # Skopiuj ćwiczenia z powtórzeniami
            for tpe in original_plan.trainingplanexercise_set.all():
                TrainingPlanExercise.objects.create(
                    training_plan=new_plan,
                    exercise=tpe.exercise,
                    repetitions=tpe.repetitions
                )
            return redirect('home')

        # Przypadek 2: Użytkownik tworzy plan od podstaw
        form = TrainingPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            # Jeśli plan tworzy trener, może oznaczyć go jako ekspercki
            if request.user.groups.filter(name='trener').exists():
                plan.is_expert = form.cleaned_data.get('is_expert', False)
            plan.save()

            # Dla każdego zaznaczonego ex_id pobieramy wartość reps_<id>
            for ex_id in request.POST.getlist('exercises'):
                try:
                    ex = Exercise.objects.get(pk=ex_id)
                except Exercise.DoesNotExist:
                    continue

                reps_str = request.POST.get(f'reps_{ex_id}', '10').strip()
                try:
                    reps = int(reps_str) if reps_str else 10
                    if reps < 1:
                        reps = 1
                except ValueError:
                    reps = 10

                TrainingPlanExercise.objects.create(
                    training_plan=plan,
                    exercise=ex,
                    repetitions=reps
                )
            return redirect('home')

    # Jeśli błąd w formularzu lub metoda inna niż POST, wracamy do 'home'
    # Ponowne renderowanie 'home' z błędami formularza jest bardziej skomplikowane,
    # więc dla uproszczenia przekierowujemy.
    return redirect('home')


@login_required
def edit_training_plan(request, pk):
    """
    Widok do edycji istniejącego planu.
    """
    plan = get_object_or_404(TrainingPlan, pk=pk)

    if request.user != plan.user and not request.user.groups.filter(name='trener').exists():
        return HttpResponseForbidden("Nie masz uprawnień do edycji tego planu.")

    if request.method == 'POST':
        # Aktualizuj podstawowe dane planu
        plan.name = request.POST.get('name', plan.name)
        plan.intensity = request.POST.get('intensity', plan.intensity)
        
        # Aktualizuj dni treningowe
        training_days = request.POST.getlist('training_days')
        plan.training_days = training_days
        
        plan.save()

        # Usuń stare ćwiczenia i dodaj nowe
        TrainingPlanExercise.objects.filter(training_plan=plan).delete()

        for ex_id in request.POST.getlist('exercises'):
            try:
                ex = Exercise.objects.get(pk=ex_id)
            except Exercise.DoesNotExist:
                continue

            reps_str = request.POST.get(f'reps_{ex_id}', '10').strip()
            try:
                reps = int(reps_str) if reps_str else 10
                if reps < 1:
                    reps = 1
            except ValueError:
                reps = 10

            TrainingPlanExercise.objects.create(
                training_plan=plan,
                exercise=ex,
                repetitions=reps
            )
        return redirect('home')

    # Ta ścieżka (GET lub błąd formularza) nie jest używana przy podejściu z popupem,
    # ale można ją zaimplementować do osobnej strony edycji.
    return redirect('home')


@login_required
def delete_training_plan(request, pk):
    plan = get_object_or_404(TrainingPlan, pk=pk)
    if plan.user != request.user and not request.user.groups.filter(name='trener').exists():
        return HttpResponseForbidden("Nie masz uprawnień do usunięcia tego planu.")
    if request.method == "POST":
        plan.delete()
    return redirect('home')


@login_required
def update_training_plan(request, pk):
    plan = get_object_or_404(TrainingPlan, pk=pk)
    if plan.user != request.user:
        return HttpResponseForbidden("Nie masz uprawnień do edycji tego planu.")
    if request.method == "POST":
        form = TrainingPlanNotesForm(request.POST, instance=plan)
        if form.is_valid():
            plan.notes = form.cleaned_data['notes']
            plan.send_notification = form.cleaned_data.get('send_notification', False)
            plan.save(update_fields=['notes', 'send_notification'])
    return redirect('home')


@login_required
def update_trainer_notes(request, pk):
    plan = get_object_or_404(TrainingPlan, pk=pk)
    if not request.user.groups.filter(name='trener').exists():
        return HttpResponseForbidden("Nie masz uprawnień do edycji notatek trenera.")
    if request.method == "POST":
        form = TrainingPlanTrainerNotesForm(request.POST, instance=plan)
        if form.is_valid():
            plan.trainer_notes = form.cleaned_data['trainer_notes']
            plan.save(update_fields=['trainer_notes'])
    return redirect('home')

@login_required
def mark_training_plan_done(request, plan_id):
    plan = get_object_or_404(TrainingPlan, id=plan_id)

    if plan.user != request.user:
        return HttpResponseForbidden("Nie masz uprawnień do oznaczenia tego planu jako wykonanego.")

    if request.method == 'POST':
        done_date_str = request.POST.get('done_date')
        done_date = parse_date(done_date_str)

        if not done_date:
            messages.error(request, "Nieprawidłowa data.")
            return redirect('home')

        # Create or update the completed record
        completed_record = TrainingPlanCompletion.objects.update_or_create(
            training_plan=plan,
            user=request.user,
            defaults={'date_completed': done_date}
        )
        
        print(f"Completed record {completed_record}")

        messages.success(request, f"Plan treningowy oznaczony jako wykonany dnia {done_date}.")
        return redirect('home')

    return redirect('home')