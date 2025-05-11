from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from .forms import TrainingPlanForm
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
    form = TrainingPlanForm(request.POST)
    #return render(request, 'home.html', {'form': form})
    training_plans = []
    
    if request.user.is_authenticated:
        training_plans = TrainingPlan.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'training_plans': training_plans
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
        form = TrainingPlanForm(request.POST, user=request.user)
        if form.is_valid():
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