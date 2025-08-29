from django.shortcuts import render
from modules.models import Modulo
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required


def home(request):
    modulos = Modulo.objects.all()
    return render(request, 'core/home.html', {'modulos': modulos})

class CustomLoginView(LoginView):
    template_name = 'core/login.html'

def home_view(request):
    modulos = Modulo.objects.all()
    return render(request, 'core/home.html', {'modulos': modulos})

def home(request):
    return render(request, 'core/index.html')
