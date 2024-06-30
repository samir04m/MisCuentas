from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('crearRecibo/', crearRecibo, name='crearRecibo'),
    path('recibo/<int:id>/', vistaRecibo, name='vistaRecibo'),
    path('recibosPeriodo/<int:periodoId>/', recibosPeriodo, name='recibosPeriodo'),
]
