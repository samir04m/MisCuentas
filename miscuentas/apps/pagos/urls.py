from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('', pagos_recurrentes, name='listado'),
    path('spotify', pago_spotify, name='spotify'),

]