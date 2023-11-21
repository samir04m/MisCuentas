from django.urls import path, include
from .views import *

urlpatterns = [
    path('token/', generarToken, name='generarToken'),
    path('resumenPrestamos/<str:token>/', resumenPrestamos, name='resumenPrestamos'),
]
