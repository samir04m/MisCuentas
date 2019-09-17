from django.urls import path, include
from .views import *

urlpatterns = [
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('registro-exitoso/', confirm_registro, name='confirm_registro'),

]
