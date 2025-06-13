# website/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import TrainingPlanForm, TrainingPlanNotesForm, TrainingPlanTrainerNotesForm
from .models import TrainingPlan, TrainingPlanExercise, Exercise


def home(request):
    """
    Wyświetla stronę główną (home.html) z listą planów i popupem do tworzenia nowego planu.
    """
    form = TrainingPlanForm()
    training_plans = []
    user = request.user
    is_trainer = False

    if user.is_authenticated:
        is_trainer = user.groups.filter(name='trener').exists()
        training_plans = (
            TrainingPlan.objects.all()
            if is_trainer
            else TrainingPlan.objects.filter(user=user)
        )

    # Pobieramy WSZYSTKIE ćwiczenia, by wyświetlić je w popupie
    all_exercises = Exercise.objects.all().order_by('name')

    return render(request, 'home.html', {
        'form': form,
        'training_plans': training_plans,
        'is_trainer': is_trainer,
        'all_exercises': all_exercises,
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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Konto utworzone dla {username}! Jesteś teraz zalogowany.')
                return redirect('home')
            else:
                messages.error(request, "Problem z automatycznym logowaniem.")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def create_training_plan(request):
    """
    Widok do obsługi POST z formularza w popupie (home.html).
    Zapisuje nowy TrainingPlan i TrainingPlanExercise według zaznaczonych checkboxów + wartości reps_<id>.
    """
    if request.method == 'POST':
        form = TrainingPlanForm(request.POST, user=request.user)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()

            # Dla każdego zaznaczonego ex_id pobieramy wartość reps_<id>
            for ex_id in request.POST.getlist('exercises'):
                try:
                    ex = Exercise.objects.get(pk=ex_id)
                except Exercise.DoesNotExist:
                    continue

                reps_str = request.POST.get(f'reps_{ex_id}', '').strip()
                try:
                    reps = int(reps_str)
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

    # Jeśli nie jest POST lub form niepoprawny, po prostu wróć do home.html
    form = TrainingPlanForm(user=request.user)
    # Ponownie musimy przekazać all_exercises i stan is_trainer / training_plans,
    # żeby popup wyświetlił się poprawnie.
    training_plans = TrainingPlan.objects.filter(user=request.user)
    is_trainer = request.user.groups.filter(name='trener').exists()
    all_exercises = Exercise.objects.all().order_by('name')

    return render(request, 'home.html', {
        'form': form,
        'training_plans': training_plans,
        'is_trainer': is_trainer,
        'all_exercises': all_exercises,
    })


@login_required
def edit_training_plan(request, pk):
    """
    Widok do edycji istniejącego planu (analogicznie do create, ale z wczytaniem/aktualizacją TrainingPlanExercise).
    Przy błędzie (form invalid) również renderuje home.html z popupem lub innym mechanizmem (lub redirect).
    """
    plan = get_object_or_404(TrainingPlan, pk=pk)

    # Sprawdź uprawnienia: tylko właściciel lub trener mogą edytować
    if request.user != plan.user and not request.user.groups.filter(name='trener').exists():
        return HttpResponseForbidden("Nie masz uprawnień do edycji tego planu.")

    # Przygotowanie: słownik {exercise_id: repetitions}, aby prewypełnić pola przy edycji
    existing_tpe = TrainingPlanExercise.objects.filter(training_plan=plan)
    reps_dict = {str(tpe.exercise_id): tpe.repetitions for tpe in existing_tpe}

    if request.method == 'POST':
        form = TrainingPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            # Kasujemy stare wpisy i wstawiamy nowe zgodnie z POST
            TrainingPlanExercise.objects.filter(training_plan=plan).delete()

            for ex_id in request.POST.getlist('exercises'):
                try:
                    ex = Exercise.objects.get(pk=ex_id)
                except Exercise.DoesNotExist:
                    continue

                reps_str = request.POST.get(f'reps_{ex_id}', '').strip()
                try:
                    reps = int(reps_str)
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
    else:
        form = TrainingPlanForm(instance=plan)

    # Ponownie potrzebne do wyrenderowania popupu w GET (lub w razie form invalid)
    training_plans = TrainingPlan.objects.filter(user=request.user)
    is_trainer = request.user.groups.filter(name='trener').exists()
    all_exercises = Exercise.objects.all().order_by('name')

    return render(request, 'home.html', {
        'form': form,
        'training_plans': training_plans,
        'is_trainer': is_trainer,
        'all_exercises': all_exercises,
        'plan': plan,          # aby popup wiedział, że jest to edycja
        'reps_dict': reps_dict # aby w popupie wstawić istniejące wartości repetitions
    })


@login_required
def delete_training_plan(request, pk):
    plan = get_object_or_404(TrainingPlan, pk=pk)
    if plan.user != request.user:
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
            plan.send_notification = form.cleaned_data['send_notification']
            plan.save(update_fields=['notes', 'send_notification'])
            return redirect('home')
    return redirect('home')


@login_required
def update_trainer_notes(request, pk):
    plan = get_object_or_404(TrainingPlan, pk=pk)
    is_trainer = request.user.groups.filter(name='trener').exists()
    if not is_trainer:
        return HttpResponseForbidden("Nie masz uprawnień do edycji tego planu.")
    if request.method == "POST":
        form = TrainingPlanTrainerNotesForm(request.POST, instance=plan)
        if form.is_valid():
            plan.trainer_notes = form.cleaned_data['trainer_notes']
            plan.save(update_fields=['trainer_notes'])
            return redirect('home')
    return redirect('home')
