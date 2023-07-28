from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from apps.contabilidad.models import *
from apps.contabilidad.myFuncs import *
from apps.usuario.userSettingFuncs import getUserSetting, getUndefinedUserSettings

@login_required
def pagos_recurrentes(request):
    return render(request, 'pagos/pagos_recurrentes.html')

@login_required
def pago_hbomax(request):
    error = ''
    valoresSinDefinir = getUndefinedUserSettings(['Nequi_CuentaId', 'PagoHboMax_PersonaId', 'PagoHboMax_Cantidad', 'GastoMensual_EtiquetaId'], request.user)
    if valoresSinDefinir:
        error = "No se han definido los siguentes datos: " + valoresSinDefinir
    else:
        cuentaId = getUserSetting('Nequi_CuentaId', request.user)
        personaId = getUserSetting('PagoHboMax_PersonaId', request.user)
        cantidad = getUserSetting('PagoHboMax_Cantidad', request.user) / 2
        etiquetaId = getUserSetting('GastoMensual_EtiquetaId', request.user)
        info = 'Pago HBO Max'
        cuenta = Cuenta.objects.filter(id=cuentaId, user=request.user).first()
        persona = Persona.objects.filter(id=personaId, user=request.user).first()
        etiqueta = Etiqueta.objects.filter(id=etiquetaId, user=request.user).first()
        if cuenta and persona and etiqueta:
            try:
                with transaction.atomic():
                    transaccionEgreso = crearTransaccion('egreso', cuenta, cantidad, info, etiqueta.nombre, 1, request.user)
                    prestamo = crearPrestamo('yopresto', cantidad, info, cuenta, persona)
            except Exception as ex:
                print(ex)
                error = 'No se pudo realizar el pago debido a un error'
        else:
            if not cuenta:
                error += f"No existe cuenta {cuentaId}. "
            if not persona:
                error += f'No existe la persona con id {personaId}. '
            if not etiqueta:
                error += f'No existe la etiqueta con id {etiquetaId}. '
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')    
    return redirect('pagos:listado')

@login_required
def pago_spotify(request):
    error = ''
    valoresSinDefinir = getUndefinedUserSettings(['Nequi_CuentaId', 'PagoSpotify_Cantidad', 'GastoMensual_EtiquetaId'], request.user)
    if valoresSinDefinir:
        error = "No se han definido los siguentes datos: " + valoresSinDefinir
    else:
        cuentaId = getUserSetting('Nequi_CuentaId', request.user)
        cantidad = getUserSetting('PagoSpotify_Cantidad', request.user)
        etiquetaId = getUserSetting('GastoMensual_EtiquetaId', request.user)
        info = 'Pago Spotify'
        cuenta = Cuenta.objects.filter(id=cuentaId, user=request.user).first()
        etiqueta = Etiqueta.objects.filter(id=etiquetaId, user=request.user).first()
        if cuenta and etiqueta:
            try:
                with transaction.atomic():
                    transaccionEgreso = crearTransaccion('egreso', cuenta, cantidad, info, etiqueta.nombre, 1, request.user)
            except Exception as ex:
                print(ex)
                error = 'No se pudo realizar el pago debido a un error'
        else:
            if not cuenta:
                error += f"No existe cuenta {cuentaId}. "
            if not etiqueta:
                error += f'No existe la etiqueta con id {etiquetaId}. '
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')
    return redirect('pagos:listado')

@login_required
def pago_internet(request):
    error = ''
    valoresSinDefinir = getUndefinedUserSettings(['Bancolombia_CuentaId', 'Andy_PersonaId', 'PagoInternet_CantidadYo', 'PagoInternet_CantidadPersona', 'GastoMensual_EtiquetaId'], request.user)
    if valoresSinDefinir:
        error = "No se han definido los siguentes datos: " + valoresSinDefinir
    else:
        cuentaId = getUserSetting('Bancolombia_CuentaId', request.user)
        personaId = getUserSetting('Andy_PersonaId', request.user)
        cantidadYo = getUserSetting('PagoInternet_CantidadYo', request.user)
        cantidadPersona = getUserSetting('PagoInternet_CantidadPersona', request.user)
        etiquetaId = getUserSetting('GastoMensual_EtiquetaId', request.user)
        info = 'Pago Internet'
        cuenta = Cuenta.objects.filter(id=cuentaId, user=request.user).first()
        persona = Persona.objects.filter(id=personaId, user=request.user).first()
        etiqueta = Etiqueta.objects.filter(id=etiquetaId, user=request.user).first()
        if cuenta and persona and etiqueta:
            try:
                with transaction.atomic():
                    transaccionEgreso = crearTransaccion('egreso', cuenta, cantidadYo, info, etiqueta.nombre, 1, persona.user)
                    prestamo = crearPrestamo('yopresto', cantidadPersona, info, cuenta, persona)
            except Exception as ex:
                error = 'No se pudo realizar el pago debido a un error'
        else:
            if not cuenta:
                error += f"No existe cuenta con id {cuentaId}. "
            if not persona:
                error += f'No existe la persona con id {personaId}. '
            if not etiqueta:
                error += f'No existe la etiqueta con id {etiquetaId}. '
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')    
    return redirect('pagos:listado')

@login_required
def pago_cuotamoto(request):
    error = ''
    valoresSinDefinir = getUndefinedUserSettings(['Bancolombia_CuentaId', 'Andy_PersonaId', 'PagoCuotaMoto_Cantidad'], request.user)
    if valoresSinDefinir:
        error = "No se han definido los siguentes datos: " + valoresSinDefinir
    else:
        cuentaId = getUserSetting('Bancolombia_CuentaId', request.user)
        personaId = getUserSetting('Andy_PersonaId', request.user)
        cantidad = getUserSetting('PagoCuotaMoto_Cantidad', request.user)
        info = 'Pago cuota moto'
        cuenta = Cuenta.objects.filter(id=cuentaId, user=request.user).first()
        persona = Persona.objects.filter(id=personaId, user=request.user).first()
        if cuenta and persona:
            try:
                with transaction.atomic():
                    prestamo = crearPrestamo('yopresto', cantidad, info, cuenta, persona)
            except Exception as ex:
                error = 'No se pudo realizar el pago debido a un error'
        else:
            if not cuenta:
                error += f"No existe cuenta con id {cuentaId}. "
            if not persona:
                error += f'No existe la persona con id {personaId}. '
    
    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Pago exitoso', extra_tags='success')
    return redirect('pagos:listado')