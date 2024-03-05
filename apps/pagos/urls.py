from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('', pagos_recurrentes, name='listado'),
    path('hbomax', pago_hbomax, name='hbomax'),
    path('spotify', pago_spotify, name='spotify'),
    path('cuota-moto', pago_cuotamoto, name='cuotamoto'),
    path('internet', pago_internet, name='internet'),
    path('apartamento', pago_apartamento, name='pago_apartamento'),
    path('establecerFechaPagos', establecerFechaPagos, name='establecerFechaPagos'),
]