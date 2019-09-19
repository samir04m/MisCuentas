from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('diario/', diario, name='diario'),
    path('mensual/', mensual, name='mensual'),
]
