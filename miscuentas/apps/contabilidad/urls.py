from django.urls import path, include
from .views import *

urlpatterns = [
    path('', panel, name='panel'),
    path('crear-cuenta', crear_cuenta, name='crear_cuenta'),
    path('crear-persona', crear_persona, name='crear_persona'),
    path('<int:cuenta_id>/crear-egreso/', crear_egreso, name='crear_egreso'),

]
