from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from .forms import TrainingPlanForm, TrainingPlanNotesForm, TrainingPlanTrainerNotesForm
from .models import TrainingPlan




# Widok rejestracji
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
                messages.success(request, f'Konto zostało utworzone dla {username}! Jesteś teraz zalogowany.')
                return redirect('home')
            else:
                messages.error(request, "Wystąpił problem z automatycznym logowaniem.")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def home(request):
    form = TrainingPlanForm()
    #return render(request, 'home.html', {'form': form})
    training_plans = []
    expert_plans = []
    user = request.user
    is_trainer = False

    if user.is_authenticated:
        is_trainer = user.groups.filter(name='trener').exists()
        training_plans = TrainingPlan.objects.all() if is_trainer else TrainingPlan.objects.filter(user=user)
        expert_plans = TrainingPlan.objects.filter(is_expert=True)

    context = {
        'form': form,
        'training_plans': training_plans,
        'expert_plans': expert_plans,
        'is_trainer': is_trainer
    }
    
    return render(request, 'home.html', context)


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


def create_training_plan(request):
    if request.method == 'POST':
        print("Otrzymane dane POST:", request.POST) 
        form = TrainingPlanForm(request.POST, user=request.user)
        expert_plan_id = request.POST.get('plan_id')
        if expert_plan_id:
            print()
            original_plan = get_object_or_404(TrainingPlan, id=expert_plan_id, is_expert=True)

            # Stwórz nową instancję dla zalogowanego użytkownika, kopiując dane
            new_plan_for_user = TrainingPlan.objects.create(
                user=request.user,
                name=original_plan.name,
                intensity=original_plan.intensity,
                training_days=original_plan.training_days,
                is_expert=False  # Nowy plan nie jest już szablonem eksperckim
            )
            new_plan_for_user.exercises.set(original_plan.exercises.all())
            return redirect('home') 
            
        if form.is_valid():
            print("form valid")
            trainig_plan = form.save(commit=False)
            trainig_plan.user = request.user  # Przypisanie user_id
            trainig_plan.save()
            form.save_m2m()
            return redirect('home')  # Zmień na swoją stronę
    else:
        form = TrainingPlanForm(user=request.user)

    return render(request, 'workout_plan_form.html', {'form': form})

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
            plan.save(update_fields=['notes','send_notification'])
            return redirect('home')
    else:
        form = TrainingPlanForm(instance=plan)
    return redirect('home')

@login_required
def update_trainer_notes(request, pk):
    is_trainer = False
    plan = get_object_or_404(TrainingPlan, pk=pk)
    is_trainer = request.user.groups.filter(name='trener').exists()
    print("Grupy użytkownika:", request.user.groups.all())

    if not is_trainer:
        return HttpResponseForbidden("Nie masz uprawnień do edycji tego planu.")
    if request.method == "POST":
        form = TrainingPlanTrainerNotesForm(request.POST, instance=plan)
        if form.is_valid():
            plan.notes = form.cleaned_data['trainer_notes']
            plan.save(update_fields=['trainer_notes'])
            return redirect('home')
    else:
        form = TrainingPlanTrainerNotesForm(instance=plan)
    return redirect('home')