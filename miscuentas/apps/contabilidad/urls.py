from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('', panel, name='panel'),
    path('crear-cuenta', crear_cuenta, name='crear_cuenta'),

    path('crear-persona', crear_persona, name='crear_persona'),
    path('<int:persona_id>/vista-persona', vista_persona, name='vista_persona'),
    path('administar-personas', listar_personas, name='listar_personas'),
    path('editar-persona/<int:pk>', login_required(EditarPersona.as_view()), name = 'editar_persona'),
    path('eliminar-persona/<int:pk>', login_required(EliminarPersona.as_view()), name = 'eliminar_persona'),

    path('listar-prestamos', listar_prestamos, name='listar_prestamos'),
    path('<int:prestamo_id>/vista-prestamo', vista_prestamo, name='vista_prestamo'),
    path('<int:prestamo_id>/cancelar-prestamo', cancelar_prestamo, name='cancelar_prestamo'),

    path('crear-etiqueta', crear_etiqueta, name='crear_etiqueta'),
    path('administar-etiquetas', listar_etiquetas, name='listar_etiquetas'),
    path('editar-etiqueta/<int:pk>', login_required(EditarEtiqueta.as_view()), name = 'editar_etiqueta'),
    path('eliminar-etiqueta/<int:pk>', login_required(EliminarEtiqueta.as_view()), name = 'eliminar_etiqueta'),

    path('todos-mis-movimientos/', todos_movimientos, name='todos_movimientos'),
    path('movimientos-cuenta/<int:cuenta_id>/', movimientos_cuenta, name='movimientos_cuenta'),
    path('movimientos-etiqueta/<int:etiqueta_id>/', movimientos_etiqueta, name='movimientos_etiqueta'),
    path('<int:transaccion_id>/vista-transaccion', vista_transaccion, name='vista_transaccion'),

    path('<int:cuenta_id>/crear-egreso/', crear_egreso, name='crear_egreso'),
    path('<int:cuenta_id>/crear-ingreso/', crear_ingreso, name='crear_ingreso'),
    path('<int:persona_id>/crear-prestamo/', crear_prestamo, name='crear_prestamo'),

    path('reporte-diario/', reporte_diario, name='reporte_diario'),

]
