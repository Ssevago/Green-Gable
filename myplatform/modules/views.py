from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    return HttpResponse("¡Hola desde la app modules!")

def base_view(request):
    return render(request, 'modules/base.html')
