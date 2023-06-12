from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *
from .viewsHelpers import *

urlpatterns = [
    path('', panel, name='inicio'),
    path('crear-cuenta/', crear_cuenta, name='crear_cuenta'),
    path('crear-egreso/<int:cuenta_id>/', crear_egreso, name='crear_egreso'),
    path('crear-ingreso/<int:cuenta_id>/', crear_ingreso, name='crear_ingreso'),
    path('crear-transferencia/<int:cuenta_id>/', transferir, name='transferir'),

    path('crear-persona/', crear_persona, name='crear_persona'),
    path('persona/<int:persona_id>/', vista_persona, name='vista_persona'),
    path('administar-personas', listar_personas, name='listar_personas'),
    path('editar-persona/<int:pk>/', login_required(EditarPersona.as_view()), name = 'editar_persona'),
    path('eliminar-persona/<int:pk>/', login_required(EliminarPersona.as_view()), name = 'eliminar_persona'),

    path('prestamos/', listar_prestamos, name='listar_prestamos'),
    path('prestamo/<int:prestamo_id>/', vista_prestamo, name='vista_prestamo'),
    path('crear-prestamo/<int:persona_id>/', crear_prestamo, name='crear_prestamo'),
    path('pagar-prestamo/<int:prestamo_id>/', pagar_prestamo, name='pagar_prestamo'),
    path('pagar-conjunto-prestamos/<int:persona_id>/', pagarConjuntoPrestamos, name='pagarConjuntoPrestamos'),
    path('eliminar-prestamo/<int:prestamo_id>/', eliminar_prestamo, name='eliminar_prestamo'),

    path('crear-etiqueta/', crear_etiqueta, name='crear_etiqueta'),
    path('administar-etiquetas', listar_etiquetas, name='listar_etiquetas'),
    path('editar-etiqueta/<int:pk>/', login_required(EditarEtiqueta.as_view()), name = 'editar_etiqueta'),
    path('eliminar-etiqueta/<int:pk>/', login_required(EliminarEtiqueta.as_view()), name = 'eliminar_etiqueta'),

    path('movimientos/', todos_movimientos, name='todos_movimientos'),
    path('movimientos-cuenta/<int:cuenta_id>/', movimientos_cuenta, name='movimientos_cuenta'),
    path('movimientos-dia/<str:tipo>/<str:fecha>/', movimientos_dia, name='movimientos_dia'),
    path('movimientos-mes/<str:tipo>/<str:fecha>/', movimientos_mes, name='movimientos_mes'),
    path('movimientos-etiqueta/<int:etiqueta_id>/', movimientos_etiqueta, name='movimientos_etiqueta'),
    path('movimientos-etiqueta-mes/<str:etiqueta_id>/<str:tipo>/<str:periodo>/', movimientos_etiqueta_mes, name='movimientos_etiqueta_mes'),

    path('transaccion/<int:transaccion_id>/', vista_transaccion, name='vista_transaccion'),
    path('transaccion-rollback/<int:transaccion_id>/', transaccion_rollback, name='transaccion_rollback'),
    path('transacciones-programadas/', transacciones_programadas, name='transacciones_programadas'),
    path('crear-transaccion-programada/', crear_transaccion_programada, name='crear_transaccion_programada'),

    path('relacionarUsuarioConTransaccion/', relacionarUsuarioConTransaccion, name='relacionarUsuarioConTransaccion'),

    path('crear-creditCard/', crear_creditCard, name='crear_creditCard'),
    path('creditCard/<int:creditCard_id>/', vista_creditCard, name='vista_creditCard'),
    path('listar-creditcards/', listar_creditCards, name='listar_creditCards'),
    path('crear-compra/<int:creditCard_id>/', crear_compra, name='crear_compra'),
    path('compra-detalles/<int:compra_id>/', vista_compra, name='vista_compra'),
    path('pagar-tarjeta/<int:tarjeta_id>/', pagar_tarjeta, name='pagar_tarjeta'),
    path('eliminar-compra/<int:compra_id>/', eliminar_compra, name='eliminar_compra'),
]
