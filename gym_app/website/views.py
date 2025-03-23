from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages

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
    return render(request, 'home.html')


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
