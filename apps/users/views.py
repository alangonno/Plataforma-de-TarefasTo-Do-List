from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserAuthenticationForm

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    authentication_form = UserAuthenticationForm 

    def get_success_url(self):
        return reverse_lazy('home')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Autentica o usuário após o registro.  
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')
