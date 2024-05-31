from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Sum
from django.http import request
from typing import List
from .models import *
from .forms import *
from .myFuncs import *
from .enums import *
from apps.usuario.views import getUserSetting, createUserNotification, NotificationType
from apps.usuario.models import UserPersona

@login_required
def vista_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    userpersona = UserPersona.objects.filter(persona=prestamo.persona, user=request.user).first()
    # solicitudesPagoPrestamo = SolicitudPagoPrestamo.objects.filter()
    context = {
        "prestamo":prestamo,
        "transaccionesPago":TransaccionPrestamo.objects.filter(prestamo=prestamo, tipo=2).all(),
        "userpersona":userpersona,
        "solicitudes":SolicitudPagoPrestamo.objects.filter(prestamo=prestamo).all()
    }
    return render(request, 'contabilidad/prestamo/vista_prestamo.html', context)

@login_required
def listar_prestamos(request):
    prestamos = Prestamo.objects.filter(persona__user = request.user.id)
    if prestamos:
        saldoTotal = Cuenta.objects.filter(user=request.user).aggregate(Sum('saldo'))
        yoDebo = Prestamo.objects.filter(persona__user=request.user.id, tipo='meprestan', cancelada=False).aggregate(Sum('saldo_pendiente'))
        meDeben = Prestamo.objects.filter(persona__user=request.user.id, tipo='yopresto', cancelada=False).aggregate(Sum('saldo_pendiente'))
        saldoTotal = saldoTotal['saldo__sum']
        yoDebo = yoDebo['saldo_pendiente__sum'] if yoDebo['saldo_pendiente__sum'] else 0
        meDeben = meDeben['saldo_pendiente__sum'] if meDeben['saldo_pendiente__sum'] else 0
        saldoRestante = saldoTotal
        pagandoPrestamosMeQueda = 0
        pagandoPrestamosMensaje = "Pagados todos los prestamos "
        pagandoPrestamosMeQueda = meDeben-yoDebo
        if pagandoPrestamosMeQueda >= 0:
            saldoRestante += pagandoPrestamosMeQueda
            pagandoPrestamosMensaje += " recuperaria"
        elif pagandoPrestamosMeQueda < 0:
            saldoRestante -= abs(pagandoPrestamosMeQueda)
            pagandoPrestamosMensaje += " tendria que pagar"
        context = {
            'prestamos':prestamos,
            'saldoTotal':saldoTotal,
            'yoDebo': yoDebo,
            'meDeben': meDeben,
            'pagandoPrestamosMensaje': pagandoPrestamosMensaje,
            'pagandoPrestamosMeQueda': abs(pagandoPrestamosMeQueda),
            'saldoRestante': saldoRestante,
            'solicitudesCreacion':SolicitudCreacionPrestamo.objects.filter(usuarioAprueba=request.user, estado=0),
            'solicitudesPago':SolicitudPagoPrestamo.objects.filter(usuarioAprueba=request.user, estado=0)
        }
    else:
        context = {
            'prestamos':prestamos
        }
    return render(request, 'contabilidad/prestamo/listar_prestamos.html', context)

@login_required
def crear_prestamo(request, persona_id):
    userpersona = UserPersona.objects.filter(persona__id=persona_id, user=request.user).first()
    user = userpersona.admin if userpersona else request.user
    persona = get_object_or_404(Persona, id=persona_id, user=user)

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        cantidad = validarMiles(int(request.POST.get('cantidad').replace('.','')))
        info = request.POST.get('info')
        cuenta = getCuentaFromPost(request)
        fecha = getDate(request.POST.get('datetime'))
        try:
            if not userpersona:
                prestamoCreado = crearPrestamo(request, tipo, cantidad, info, cuenta, persona, fecha)
                return redirect('panel:vista_prestamo', prestamoCreado.id)
            else:
                crearSolicitudCreacionPrestamo(tipo, cantidad, info, cuenta, persona, fecha, userpersona)
                alert(request, 'Se ha enviado la solicitud de creación del prestamo. Este sera creado una vez la persona involucrada lo apruebe.')
        except Exception as e:
            alert(request, e, 'e')

        return redirect('panel:vista_persona', persona_id)      

    context = {
        "cuentas":selectCuentas(request, userpersona), 
        "persona":persona,
        "mostrarSaldoCuentas":getUserSetting('MostrarSaldoCuentas', request.user),
        "tiposPrestamos":getTipoPrestamoSelect(userpersona),
        "userpersona":userpersona
    }
    return render(request, 'contabilidad/prestamo/crear_prestamo.html', context)

@login_required
def pagar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    userpersona = UserPersona.objects.filter(persona=prestamo.persona, user=request.user).first()

    if request.method == 'POST':
        monto = int(request.POST.get('monto').replace('.',''))
        # monto = validarMiles(monto)
        try:
            with transaction.atomic():
                procesarPagoPrestamo(prestamo, monto, request)
        except Exception as ex:
            printException(ex)
        return redirect('panel:vista_prestamo', prestamo_id)
    else:
        cuentas = selectCuentas(request, userpersona)
        tags = Etiqueta.objects.filter(user=request.user).exclude(nombre='Prestamo').exclude(nombre='Transferencia')
        context = {
            "prestamo":prestamo, 
            "cuentas": cuentas, 
            "saldo_pendiente": prestamo.saldo_pendiente,
            "tags": tags,
            "userpersona": userpersona
        }
        return render(request, 'contabilidad/prestamo/pagar_prestamo.html', context)

@login_required
def eliminar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    personaId = prestamo.persona.id
    if prestamo.cuenta:
        transaccion = Transaccion.objects.get(cuenta=prestamo.cuenta, fecha=prestamo.fecha)
        if transaccion:
            for tp in prestamo.transaccionprestamo_set.all():
                transaccionPartePago = tp.transaccion
                eliminarTransaccion(transaccionPartePago)
            eliminarTransaccion(transaccion)
    else:
        transaccionPrestamo = TransaccionPrestamo.objects.filter(prestamo=prestamo)
        for tp in transaccionPrestamo:
            transaccion = tp.transaccion
            transaccion.delete()
            tp.delete()

    prestamo.delete()
    alert(request, 'Se ha eliminado el prestamo')
    return redirect("panel:vista_persona", personaId)

@login_required
def pagarConjuntoPrestamos(request, persona_id):
    if request.method == 'POST':
        pagoTotal = validarMiles(int(request.POST.get('pagoTotal').replace('.','')))
        if pagoTotal <= 0:
            alert(request, 'El total a pagar debe ser mayor a cero', 'e')
            return redirect('panel:vista_persona', persona_id)
        
        persona = get_object_or_404(Persona, id=persona_id)
        tipoPrestamo = request.POST.get('tipoPrestamo')
        cuenta = getCuentaFromPost(request)
        info = request.POST.get('info')
        user = request.user
        fechaPago = getDate(request.POST.get('datetime'))
        userpersona = UserPersona.objects.filter(persona__id=persona_id, user=user).first()
        if not userpersona:
            transaccion = pagarMultiplesPrestamos(request, pagoTotal, cuenta, fechaPago, user, tipoPrestamo, persona_id)
            crearNotificacionPagoPrestamoFromTransaccion(transaccion, info, persona)
        else:
            crearSolicitudPagoMultiplesPrestamos(pagoTotal, cuenta, info, userpersona, fechaPago, tipoPrestamo, persona)
            alert(request, 'Se ha creado la solicitud de pago multiple. Cuando la persona involucrada la acepte se vera reflejado el pago.')
    return redirect('panel:vista_persona', persona_id)

def pagarMultiplesPrestamos(request, pagoTotal:int, cuenta:Cuenta, fechaPago:str, user:User, tipoPrestamo:str, personaId:int) -> Transaccion:
    prestamos = Prestamo.objects.filter(tipo=tipoPrestamo, persona__id=personaId, cancelada=False).order_by('fecha')
    disponible = pagoTotal
    transaccionPadre = None
    try:
        with transaction.atomic():
            for prestamo in prestamos:
                if disponible >= prestamo.saldo_pendiente:
                    monto = prestamo.saldo_pendiente
                else:
                    monto = disponible
                disponible -= monto
                transaccionNueva = pagarPrestamo(prestamo, monto, cuenta, "", fechaPago, user)
                
                if transaccionPadre:
                    transaccionPadre = crearGrupoTransaccion(request, transaccionPadre, transaccionNueva)
                else:
                    transaccionPadre = transaccionNueva # Solo se iguala la primera vez

                if disponible == 0:
                    break
        alert(request, 'Pago de multiples prestamos realizado')
        return transaccionPadre
    except Exception as ex:
        printException(ex)
        alert(request, 'Ocurrio un error', 'e')
        return None

@login_required
def vistaSolicitudesPrestamos(request):
    solicitudesCreacion = SolicitudCreacionPrestamo.objects.filter(usuarioAprueba=request.user)
    context = {
        'solicitudesCreacion': solicitudesCreacion
    }
    return render(request, 'contabilidad/prestamo/vistaSolicitudesPrestamos.html', context)


@login_required
def vistaSolicitudPagoPrestamo(request, id):
    solicitud = get_object_or_404(SolicitudPagoPrestamo, id=id)
    return render(request, 'contabilidad/prestamo/vista_solicitudPagoPrestamo.html', {"solicitud":solicitud})

@login_required
def cambiarEstadoSolicitudCreacionPrestamo(request, id, nuevoEstado):
    solicitud = get_object_or_404(SolicitudCreacionPrestamo, id=id)
    solicitud.estado = nuevoEstado
    solicitud.save()
    alert(request, 'Soliciud aprobada!' if nuevoEstado == 1 else 'Solicitud rechazada!')
    if nuevoEstado == 1:
        prestamo = crearPrestamo(request, solicitud.tipo, solicitud.valor, solicitud.info, solicitud.cuenta, solicitud.persona, solicitud.fechaPrestamo)
        return redirect('panel:vista_prestamo', prestamo.id)
    else:
        return RedireccionarVistaAnterior(request)

@login_required
def cambiarEstadoSolicitudPagoPrestamo(request, id, nuevoEstado):
    solicitud = get_object_or_404(SolicitudPagoPrestamo, id=id)
    try:
        with transaction.atomic():
            solicitud.estado = nuevoEstado
            solicitud.save()
            if nuevoEstado == 1:
                if solicitud.pagoMultiple:
                    transaccionDelPrestamo = pagarMultiplesPrestamos(request, solicitud.valor, solicitud.cuenta, solicitud.fechaPago, solicitud.usuarioAprueba, solicitud.pagoMultipleTipoPrestamo, solicitud.persona.id)
                else:
                    transaccionDelPrestamo = pagarPrestamo(solicitud.prestamo, solicitud.valor, solicitud.cuenta, solicitud.info, solicitud.fechaPago, solicitud.usuarioAprueba)
                crearNotificacionPagoPrestamoFromTransaccion(transaccionDelPrestamo, solicitud.info, solicitud.persona)

            alert(request, 'Soliciud aprobada!' if nuevoEstado == 1 else 'Solicitud rechazada!')
    except Exception as ex:
        printException(ex)
        alert(request, 'No fue posible cambiar el estado de la solicitud', 'e')
    return RedireccionarVistaAnterior(request)

def eliminarSolicitudPagoPrestamo(request, id):
    solicitud = get_object_or_404(SolicitudPagoPrestamo, id=id)
    prestamo = solicitud.prestamo
    solicitud.delete()
    alert(request, 'La solicitud fue eliminada!')
    if prestamo:
        return redirect('panel:vista_prestamo', prestamo.id)
    else:
        return redirect('panel:inicio')

def procesarPagoPrestamo(prestamo:Prestamo, monto, request):
    userpersona = UserPersona.objects.filter(persona=prestamo.persona, user=request.user).first()
    cuenta = getCuentaFromPost(request)
    info = request.POST.get('info')
    user = request.user
    fechaPago = getDate(request.POST.get('datetime'))
    if not userpersona:
        transaccion = pagarPrestamo(prestamo, monto, cuenta, info, fechaPago, user)
        crearNotificacionPagoPrestamoFromTransaccion(transaccion, info, prestamo.persona)
    else:
        crearSolicitudPagoPrestamo(monto, info, prestamo, cuenta, userpersona, fechaPago)
        alert(request, 'Se le ha solicitado a la persona involucrada confirmar el pago. Una vez aprobado se reflejara el comprobante.')

def pagarPrestamo(prestamo:Prestamo, monto:int, cuenta:Cuenta, info:str, fechaPago:str, user:User) -> Transaccion:
    if monto > prestamo.saldo_pendiente: # Si el monto es mayor al saldo pendiente
        monto = prestamo.saldo_pendiente # El monto a pagar se iguala para que no lo supere

    prestamo.saldo_pendiente -= monto
    if prestamo.saldo_pendiente == 0:
        prestamo.cancelada = True
    prestamo.save()

    if prestamo.tipo == 'yopresto':
        if cuenta:
            cuenta.saldo += monto
        tipoTransaccion = 'ingreso'
        infoTransaccion = " pagó la totalidad del prestamo." if prestamo.cancelada else " pagó una parte del prestamo. "
        infoTransaccion = prestamo.persona.nombre + infoTransaccion
    elif prestamo.tipo == 'meprestan':
        if cuenta:
            cuenta.saldo -= monto
        tipoTransaccion = 'egreso'
        infoTransaccion = "Pagué la totalidad del prestamo con " if prestamo.cancelada else "Pagué parte del prestamo con "
        infoTransaccion += prestamo.persona.nombre + ". "
    if cuenta:
        cuenta.save()

    compraCreditoPrestamo = CompraCreditoPrestamo.objects.filter(prestamo=prestamo).first()
    if compraCreditoPrestamo:
        tag = Etiqueta.objects.filter(tipo=3).first()
    else:
        tag = getEtiquetaByName('Prestamo', user)

    transaccion = Transaccion(
        tipo = tipoTransaccion,
        saldo_anterior = cuenta.saldo if cuenta else 0,
        cantidad = monto,
        info = infoTransaccion + "\n" + info if info else "",
        cuenta = cuenta,
        etiqueta = tag,
        fecha = fechaPago,
        user = user
    )
    transaccion.save()
    transaccionPrestamo = TransaccionPrestamo(transaccion=transaccion, prestamo=prestamo)
    transaccionPrestamo.save()
    return transaccion

def crearSolicitudPagoPrestamo(valor:int, info:str, prestamo:Prestamo, cuenta:Cuenta, userpersona:UserPersona, fechaPago:str):
    solicitud = SolicitudPagoPrestamo(
        valor = valor,
        info = info,
        prestamo = prestamo,
        cuenta = cuenta,
        persona = prestamo.persona,
        fechaPago = fechaPago,
        pagoMultiple = False,
        usuarioSolicita = userpersona.user,
        usuarioAprueba = userpersona.admin,
        fechaSolicitud = datetime.now()
    )
    solicitud.save()

def crearSolicitudPagoMultiplesPrestamos(valor:int, cuenta:Cuenta, info:str, userpersona:UserPersona, fechaPago:str, tipoPrestamo:str, persona:Persona):
    solicitud = SolicitudPagoPrestamo(
        valor = valor,
        cuenta = cuenta,
        info = info,
        fechaPago = fechaPago,
        pagoMultiple = True,
        pagoMultipleTipoPrestamo = getTipoPrestamoOpuesto(tipoPrestamo),
        persona = persona,
        usuarioSolicita = userpersona.user,
        usuarioAprueba = userpersona.admin,
        fechaSolicitud = datetime.now()
    )
    solicitud.save()

def crearSolicitudCreacionPrestamo(tipo:str, valor:int, info:str, cuenta:Cuenta, persona:Persona, fecha:str, userpersona:UserPersona):
    solicitud = SolicitudCreacionPrestamo(
        tipo = tipo,
        valor = valor,
        info = info,
        cuenta = cuenta,
        persona = persona,
        fechaPrestamo = fecha,
        usuarioSolicita = userpersona.user,
        usuarioAprueba = userpersona.admin,
        fechaSolicitud = datetime.now()
    )
    solicitud.save()

class TipoPrestamo:
    def __init__(self, id:str, nombre:str):
        self.id = id
        self.nombre = nombre

def getTipoPrestamoSelect(userpersona:UserPersona) -> List[TipoPrestamo]:
    if not userpersona:
        return [
            TipoPrestamo('yopresto', 'Yo Presto'),
            TipoPrestamo('meprestan', 'Me Prestan'),
        ]
    else:
        return [
            TipoPrestamo('yopresto', 'Me Prestan'),
            TipoPrestamo('meprestan', 'Yo Presto'),
        ]

def crearNotificacionPagoPrestamo(valorPago:int, cuenta:Cuenta, infoPago:str, persona:Persona, userOwnerPrestamo:User, pagoMultiple:bool):
    nombreCuenta = cuenta.nombre if cuenta else 'Ninguna'
    mensajePago = 'varios préstamos' if pagoMultiple else 'un préstamo'
    usuariosANotificar = [userOwnerPrestamo]
    userpersona = UserPersona.objects.filter(admin=userOwnerPrestamo, persona=persona).first()
    if userpersona:
        usuariosANotificar.append(userpersona.user)

    for user in usuariosANotificar:
        if user.username == userOwnerPrestamo.username:
            nombrePersonaInvolucrada = persona.nombre
        else:
            nombrePersonaInvolucrada = userOwnerPrestamo.username
        message = '''
        Se registró el pago de {} con {}, 
        Valor del pago {}, 
        Cuenta: {}. 
        Información: {}.'''.format(mensajePago, nombrePersonaInvolucrada, getFormatoDinero(valorPago), nombreCuenta, infoPago)

        createUserNotification(message, user, NotificationType.PagoPrestamo)

def crearNotificacionPagoPrestamoFromTransaccion(transaccion:Transaccion, infoPago:str, persona:Persona):
    if transaccion:
        pagoMultiple = True if transaccion.estado == EstadoTransaccion.PadreGrupo.value else False
        crearNotificacionPagoPrestamo(transaccion.cantidad, transaccion.cuenta, infoPago, persona, transaccion.user, pagoMultiple)