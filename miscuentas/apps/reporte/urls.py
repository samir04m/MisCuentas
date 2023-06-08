from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('general/', general, name='general'),
    path('egresos-diarios/', egresos_diarios, name='egresos_diarios'),
    path('ingresos-diarios/', ingresos_diarios, name='ingresos_diarios'),
    path('egresos-mensuales/', egresos_mensuales, name='egresos_mensuales'),
    path('ingresos-mensuales/', ingresos_mensuales, name='ingresos_mensuales'),
    path('egresos-etiqueta/<int:month>/<int:year>', egresos_etiqueta, name='egresos_etiqueta'),
    path('consultar-periodo-etiquetas/', consultar_periodo_etiquetas, name='consultar_periodo_etiquetas'),
]
