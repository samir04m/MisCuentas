from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Sum
from django.http import request
from .models import *
from .forms import *
from .myFuncs import *
from apps.usuario.views import getUserSetting
from apps.usuario.models import UserPersona

@login_required
def vista_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    userpersona = UserPersona.objects.filter(persona=prestamo.persona, user=request.user).first()
    print(' ----', dir(prestamo))
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
        }
    else:
        context = {
            'prestamos':prestamos
        }
    return render(request, 'contabilidad/prestamo/listar_prestamos.html', context)

@login_required
def crear_prestamo(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id, user=request.user.id)
    mensaje = None

    if request.method == 'POST':
        request.POST._mutable = True
        form = PrestamoForm(request.POST)
        form.data['cantidad'] = int(form.data['cantidad'].replace('.',''))

        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.cantidad = validarMiles(prestamo.cantidad)
            cuenta = None
            if request.POST.get('cuenta') != 'ninguna':
                cuenta = get_object_or_404(Cuenta, id=int(request.POST.get('cuenta')), user=request.user.id)
            
            try:
                prestamoCreado = crearPrestamo(request, prestamo.tipo, prestamo.cantidad, prestamo.info, cuenta, persona, getDate(request.POST.get('datetime')))
                return redirect('panel:vista_prestamo', prestamoCreado.id)
            except Exception as e:
                messages.success(request, e, extra_tags='error')

            return redirect('panel:vista_persona', persona_id)                 
    else:
        form = PrestamoForm()

    cuentas = Cuenta.objects.filter(user=request.user.id)
    context = {
        "form": form, 
        "cuentas":cuentas, 
        "persona":persona, 
        "mensaje":mensaje,
        "mostrarSaldoCuentas":getUserSetting('MostrarSaldoCuentas', request.user)
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
            print("----- Exception -----", ex)
        return redirect('panel:vista_prestamo', prestamo_id)
    else:
        cuentas = Cuenta.objects.filter(user=request.user)
        if not cuentas and userpersona:
            cuentas = Cuenta.objects.filter(user=userpersona.admin)
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
    messages.success(request, 'Se ha eliminado el prestamo', extra_tags='success')
    return redirect("panel:vista_persona", personaId)

@login_required
def pagarConjuntoPrestamos(request, persona_id):
    if request.method == 'POST':
        pagoTotal = validarMiles(int(request.POST.get('pagoTotal').replace('.','')))
        if pagoTotal <= 0:
            if request:
                messages.error(request, 'El total a pagar debe ser mayor a cero', extra_tags='error')
            return redirect('panel:vista_persona', persona_id)
        prestamos = Prestamo.objects.filter(tipo=request.POST.get('tipoPrestamo'), persona=persona_id, cancelada=False).order_by('fecha')
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
                    # transaccionNueva = pagarPrestamo(prestamo, monto, request)
                    
                    # if transaccionPadre:
                    #     transaccionPadre = crearGrupoTransaccion(request, transaccionPadre, transaccionNueva)
                    # else:
                    #     transaccionPadre = transaccionNueva # Solo se iguala la primera vez

                    if disponible == 0:
                        break
            if request:
                messages.success(request, 'Pago de multiples prestamos realizado', extra_tags='success')
        except Exception as ex:
            print("----- Exception -----", ex)
            if request:
                messages.error(request, 'Ocurrio un error', extra_tags='error')

    return redirect('panel:vista_persona', persona_id)

@login_required
def vistaSolicitudPagoPrestamo(request, id):
    solicitud = get_object_or_404(SolicitudPagoPrestamo, id=id)
    return render(request, 'contabilidad/prestamo/vista_solicitudPagoPrestamo.html', {"solicitud":solicitud})

@login_required
def cambiarEstadoSolicitudPagoPrestamo(request, id, nuevoEstado):
    solicitud = get_object_or_404(SolicitudPagoPrestamo, id=id)
    solicitud.estado = nuevoEstado
    solicitud.save()
    if nuevoEstado == 1:
        pagarPrestamo(solicitud.prestamo, solicitud.valorPago, solicitud.cuenta, solicitud.info, solicitud.fechaPago, solicitud.user)
    messages.success(request, 'Soliciud aprobada!' if nuevoEstado == 1 else 'Solicitud rechazada!', extra_tags='success')
    return redirect('panel:vistaSolicitudPagoPrestamo', id)

def eliminarSolicitudPagoPrestamo(request, id):
    solicitud = get_object_or_404(SolicitudPagoPrestamo, id=id)
    prestamo = solicitud.prestamo
    solicitud.delete()
    messages.success(request, 'La solicitud fue eliminada!', extra_tags='success')
    if prestamo:
        return redirect('panel:vista_prestamo', prestamo.id)
    else:
        return redirect('panel:inicio')

def procesarPagoPrestamo(prestamo:Prestamo, monto, request) -> Transaccion:
    userpersona = UserPersona.objects.filter(persona=prestamo.persona, user=request.user).first()
    cuenta = getCuentaFromPost(request)
    info = request.POST.get('info')
    user = request.user
    fechaPago = request.POST.get('datetime')

    if not userpersona:
        return pagarPrestamo(prestamo, monto, cuenta, info, fechaPago, user)
    else:
        crearSolicitudPagoPrestamo(False, monto, info, prestamo, cuenta, user, fechaPago, "")
        messages.success(request, 'Se le ha solicitado a la persona involucrada confirmar el pago. Una vez aprobado se reflejara el comprobante.', extra_tags='success')
        return None

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
        fecha = getDate(fechaPago),
        user = user
    )
    transaccion.save()
    transaccionPrestamo = TransaccionPrestamo(transaccion=transaccion, prestamo=prestamo)
    transaccionPrestamo.save()
    return transaccion

def crearSolicitudPagoPrestamo(pagoMultiple:bool, valor:int, info:str, prestamo:Prestamo, cuenta:Cuenta, user:User, fechaPago:str, tipoPrestamo:str):
    solicitud = SolicitudPagoPrestamo(
        pagoMultiple = pagoMultiple,
        valorPago = valor,
        info = info,
        prestamo = prestamo,
        cuenta = cuenta,
        user = user,
        fechaPago = fechaPago,
        tipoPrestamoPagoMultiple = tipoPrestamo,
        fechaSolicitud = datetime.now()
    )
    solicitud.save()