from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from apps.contabilidad.models import *
from apps.contabilidad.myFuncs import *
from apps.usuario.userSettingFuncs import getUserSetting, getUndefinedUserSettings, setUserSetting

@login_required
def pagos_recurrentes(request):
    fechaPagos = getUserSetting('FechaPagos', request.user)
    if not fechaPagos:
        fechaPagos = ''
    return render(request, 'pagos/pagos_recurrentes.html', {'fechaPagos':fechaPagos})

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
                    transaccionEgreso = crearTransaccion(request, 'egreso', cuenta, cantidad, info, etiqueta.nombre, 1, getFechaPago(request))
                    prestamo = crearPrestamo(request, 'yopresto', cantidad, info, cuenta, persona, getFechaPago(request))
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
                    transaccionEgreso = crearTransaccion(request, 'egreso', cuenta, cantidad, info, etiqueta.nombre, 1, getFechaPago(request))
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
                    transaccionEgreso = crearTransaccion(request, 'egreso', cuenta, cantidadYo, info, etiqueta.nombre, 1, getFechaPago(request))
                    prestamo = crearPrestamo(request, 'yopresto', cantidadPersona, info, cuenta, persona, getFechaPago(request))
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
                    prestamo = crearPrestamo(request, 'yopresto', cantidad, info, cuenta, persona, getFechaPago(request))
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

@login_required
def pago_apartamento(request):
    error = ''
    valoresSinDefinir = getUndefinedUserSettings(['Jota_PersonaId', 'Manuel_PersonaId'], request.user)
    if valoresSinDefinir:
        error = "No se han definido los siguentes datos: " + valoresSinDefinir
    else:
        if request.method == 'POST':
            valor = validarMiles(int(request.POST.get('valor').replace('.','')))
            cuenta = getCuentaFromPost(request)
            info = request.POST.get('info')
            fecha = getDate(request.POST.get('datetime'))
            terceraParteValor = int(valor/3)
            ajusteDecimales = valor - (terceraParteValor*3)
            tagName = getEtiquetaFromPost(request).nombre if getEtiquetaFromPost(request) else None
            try:
                with transaction.atomic():
                    jotaPersona = Persona.objects.get(id=int(getUserSetting('Jota_PersonaId', request.user)))
                    manuelPersona = Persona.objects.get(id=int(getUserSetting('Manuel_PersonaId', request.user)))
                    prestamo1 = crearPrestamo(request, 'yopresto', terceraParteValor, info, cuenta, jotaPersona, fecha)
                    prestamo2 = crearPrestamo(request, 'yopresto', terceraParteValor, info, cuenta, manuelPersona, fecha)
                    transaccion = crearTransaccion(request, 'egreso', cuenta, terceraParteValor+ajusteDecimales, info, tagName, 1, fecha)
                    agruparTransaccionesPagoApartamento(prestamo1, prestamo2, transaccion)
            except Exception as ex:
                print("Exception: ", ex)
                error = "Ocurrio un error al intentar crear las transacciones"
        else:
            context = {
                "cuentas": selectCuentas(request),
                "tags": getSelectEtiquetas(request)
            }
            return render(request, 'pagos/pago_apartamento.html', context)

    if error:
        messages.error(request, error, extra_tags='error')
    else:
        messages.success(request, 'Se registro el pago exitosamente', extra_tags='success')
    return redirect('pagos:listado')

def agruparTransaccionesPagoApartamento(prestamo1, prestamo2, transaccion3):
    transaccionPrestamo1 = TransaccionPrestamo.objects.filter(prestamo=prestamo1).first()
    transaccionPrestamo2 = TransaccionPrestamo.objects.filter(prestamo=prestamo2).first()
    transaccionPadre = crearGrupoTransaccion(None, transaccion3, transaccionPrestamo1.transaccion)
    crearGrupoTransaccion(None, transaccionPadre, transaccionPrestamo2.transaccion)

def establecerFechaPagos(request):
    if request.method == 'POST':
        setUserSetting('FechaPagos', request.POST.get('datetime'), request.user)
    return redirect('pagos:listado')

def getFechaPago(request):
    fecha = getUserSetting('FechaPagos', request.user)
    if fecha:
        return getDate(fecha)
    else:
        return datetime.now()