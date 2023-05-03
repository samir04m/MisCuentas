from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.contabilidad.models import *
from .myFuncs import *

@login_required
def pagos_recurrentes(request):
    return render(request, 'pagos/pagos_recurrentes.html')

@login_required
def pago_hbomax(request):
    nombreCuenta = 'Nequi'
    nombrePersona = 'Jorge Ivan'
    cantidad = 25000/2
    info = 'Pago HBO Max'
    cuenta = Cuenta.objects.filter(nombre=nombreCuenta, user=request.user).first()
    persona = Persona.objects.filter(nombre=nombrePersona, user=request.user).first()
    error = ''
    if cuenta and persona:
        try:
            transaccionEgreso = crearTransaccion('egreso', cuenta, cantidad, info, 'Gasto mensual', request.user)
            prestamo = crearPrestamo('yopresto', cantidad, info, cuenta, persona)
        except Exception as ex:
            error = 'No se pudo realizar el pago debido a un error'
    else:
        if not cuenta:
            error += f"No existe cuenta {nombreCuenta}. "
        if not persona:
            error += f'No existe la persona {nombrePersona}. '
    
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')    

    return redirect('pagos:listado')

@login_required
def pago_cuotamoto(request):
    nombreCuenta = 'Bancolombia'
    nombrePersona = 'Andy'
    cantidad = 303000
    info = 'Pago cuota moto'
    cuenta = Cuenta.objects.filter(nombre=nombreCuenta, user=request.user).first()
    persona = Persona.objects.filter(nombre=nombrePersona, user=request.user).first()
    error = ''
    if cuenta and persona:
        try:
            prestamo = crearPrestamo('yopresto', cantidad, info, cuenta, persona)
        except Exception as ex:
            error = 'No se pudo realizar el pago debido a un error'
    else:
        if not cuenta:
            error += f"No existe cuenta {nombreCuenta}. "
        if not persona:
            error += f'No existe la persona {nombrePersona}. '
    
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')

    return redirect('pagos:listado')

@login_required
def pago_internet(request):
    nombreCuenta = 'Bancolombia'
    nombrePersona = 'Andy'
    info = 'Pago HBO Max'
    cuenta = Cuenta.objects.filter(nombre=nombreCuenta, user=request.user).first()
    persona = Persona.objects.filter(nombre=nombrePersona, user=request.user).first()
    error = ''
    if cuenta and persona:
        try:
            transaccionEgreso = crearTransaccion('egreso', cuenta, 55000, info, 'Gasto mensual', request.user)
            prestamo = crearPrestamo('yopresto', 50000, info, cuenta, persona)
        except Exception as ex:
            error = 'No se pudo realizar el pago debido a un error'
    else:
        if not cuenta:
            error += f"No existe cuenta {nombreCuenta}. "
        if not persona:
            error += f'No existe la persona {nombrePersona}. '
    
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')    

    return redirect('pagos:listado')