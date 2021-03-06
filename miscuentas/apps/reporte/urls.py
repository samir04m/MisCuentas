from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('diario-egreso/', diario_egreso, name='diario_egreso'),
    path('diario-ingreso/', diario_ingreso, name='diario_ingreso'),
    path('mensual-egreso/', mensual_egreso, name='mensual_egreso'),
    path('mensual-ingreso/', mensual_ingreso, name='mensual_ingreso'),
    path('etiqueta-egreso/', etiqueta_egreso, name='etiqueta_egreso'),
]
