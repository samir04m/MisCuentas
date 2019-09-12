from django.urls import path, include
from .views import *

urlpatterns = [
    path('', panel, name='panel'),
    path('crear-cuenta', crear_cuenta, name='crear_cuenta'),
    path('crear-persona', crear_persona, name='crear_persona'),
    path('crear-etiqueta', crear_etiqueta, name='crear_etiqueta'),
    path('movimientos-cuenta/<int:cuenta_id>/', movimientos_cuenta, name='movimientos_cuenta'),
    path('<int:cuenta_id>/crear-egreso/', crear_egreso, name='crear_egreso'),
    path('<int:cuenta_id>/crear-ingreso/', crear_ingreso, name='crear_ingreso'),

]
