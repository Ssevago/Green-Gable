from django.urls import path
from .views import home, CustomLoginView
from . import views


urlpatterns = [
    path('', home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', views.home_view, name='home'),
    
]
