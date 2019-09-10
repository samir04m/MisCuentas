from django.urls import path, include
from .views import *

urlpatterns = [
    path('panel', panel, name='panel'),
    path('crear-cuenta', CrearCuenta.as_view(), name='crear_cuenta'),
]
