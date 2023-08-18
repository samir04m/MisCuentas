from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('general/', general, name='general'),
    path('egresos-diarios/', egresos_diarios, name='egresos_diarios'),
    path('ingresos-diarios/', ingresos_diarios, name='ingresos_diarios'),
    path('egresos-mensuales/', egresos_mensuales, name='egresos_mensuales'),
    path('ingresos-mensuales/', ingresos_mensuales, name='ingresos_mensuales'),
    path('etiqueta/<int:month>/<int:year>', reporte_etiqueta_mensual, name='reporte_etiqueta_mensual'),
    path('cambiar_periodo_reporte_etiqueta_mensual/', cambiar_periodo_reporte_etiqueta_mensual, name='cambiar_periodo_reporte_etiqueta_mensual'),
    path('subtag/<int:etiquetaId>/<str:periodo>', reporte_subtag_mensual, name='reporte_subtag_mensual'),
    path('cambiar_periodo_reporte_subtag_mensual/', cambiar_periodo_reporte_subtag_mensual, name='cambiar_periodo_reporte_subtag_mensual'),
]
