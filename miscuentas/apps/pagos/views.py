from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.contabilidad.models import *
from .myFuncs import *

@login_required
def pagos_recurrentes(request):
    return render(request, 'pagos/pagos_recurrentes.html')

@login_required
def pago_spotify(request):
    cuenta = Cuenta.objects.filter(nombre='Nequi', user=request.user).first()
    persona = Persona.objects.filter(nombre='Jorge Ivan', user=request.user).first()
    error = ''
    cantidad = 25000/2
    info = 'Pago Spotify'
    if cuenta and persona:
        try:
            transaccionEgreso = crearTransaccion('egreso', cuenta, cantidad, info, 'Gasto mensual', request.user)
            prestamo = crearPrestamo('yopresto', cantidad, info, cuenta, persona)
        except Exception as ex:
            error = 'No se pudo realizar el pago debido a un error'
    else:
        if not cuenta:
            error += 'No existe cuenta Nequi. '
        if not persona:
            error += 'No existe Jorge Ivan. '
    
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')    

    return redirect('pagos:listado')