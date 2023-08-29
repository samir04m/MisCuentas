from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import request
from django.db.models import Sum
from .models import *
from .forms import *
from .myFuncs import *

@login_required
def vista_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    return render(request, 'contabilidad/prestamo/vista_prestamo.html', {"prestamo":prestamo})

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
    context = {"form": form, "cuentas":cuentas, "persona":persona, "mensaje":mensaje}
    return render(request, 'contabilidad/prestamo/crear_prestamo.html', context)

@login_required
def pagar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)

    if request.method == 'POST':
        monto = int(request.POST.get('monto').replace('.',''))
        monto = validarMiles(monto)
        try:
            with transaction.atomic():
                pagarPrestamo(prestamo, monto, request)
        except Exception as ex:
            print("----- Exception -----", ex)
        return redirect('panel:vista_prestamo', prestamo_id)
    else:
        cuentas = Cuenta.objects.filter(user=request.user)
        tags = Etiqueta.objects.filter(user=request.user).exclude(nombre='Prestamo').exclude(nombre='Transferencia')
        context = {
            "prestamo":prestamo, 
            "cuentas": cuentas, 
            "saldo_pendiente": prestamo.saldo_pendiente,
            "tags": tags
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
        tps = TransaccionPrestamo.objects.filter(prestamo=prestamo)
        for tp in tps:
            transaccion = tp.transaccion
            transaccion.delete()
            tp.delete()

    prestamo.delete()
    messages.success(request, 'Se ha eliminado el prestamo', extra_tags='success')
    return redirect("panel:vista_persona", personaId)

@login_required
def pagarConjuntoPrestamos(request, persona_id):
    if request.method == 'POST':
        cuentaId = int(request.POST.get('cuenta'))
        pagoTotal = int(request.POST.get('pagoTotal').replace('.',''))
        if pagoTotal <= 0:
            messages.error(request, 'El total a pagar debe ser mayor a cero', extra_tags='error')
            return redirect('panel:vista_persona', persona_id)
        prestamos = Prestamo.objects.filter(tipo=request.POST.get('tipoPrestamo'), persona=persona_id, cancelada=False).order_by('fecha')
        disponible = pagoTotal
        try:
            with transaction.atomic():
                for prestamo in prestamos:
                    if disponible >= prestamo.saldo_pendiente:
                        monto = prestamo.saldo_pendiente
                    else:
                        monto = disponible
                    disponible -= monto
                    pagarPrestamo(prestamo, monto, request)
                    if disponible == 0:
                        break
            messages.success(request, 'Pago de multiples prestamos realizado', extra_tags='success')
        except Exception as ex:
            print("----- Exception -----", ex)
            messages.error(request, 'Ocurrio un error', extra_tags='error')

    return redirect('panel:vista_persona', persona_id)

def pagarPrestamo(prestamo:Prestamo, monto, request):
    if monto > prestamo.saldo_pendiente: 
            monto = prestamo.saldo_pendiente

    prestamo.saldo_pendiente -= monto
    if prestamo.saldo_pendiente == 0:
        prestamo.cancelada = True
    prestamo.save()

    cuentaId = int(request.POST.get('cuenta'))
    if cuentaId:
        cuenta = Cuenta.objects.get(id = cuentaId)
    else:
        cuenta = None

    if cuenta: 
        saldo_anterior = cuenta.saldo
    else:
        saldo_anterior = 0

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

    tag = getEtiquetaByName('Prestamo', request.user)
    infoAdicional = "\n" + request.POST.get('info') if (request.POST.get('info')) else ""
    transaccion = Transaccion(
        tipo = tipoTransaccion,
        saldo_anterior = saldo_anterior,
        cantidad = monto,
        info = infoTransaccion + infoAdicional,
        cuenta = cuenta,
        etiqueta = tag,
        fecha = getDate(request.POST.get('datetime')),
        user = request.user
    )
    transaccion.save()
    transaccionPrestamo = TransaccionPrestamo(transaccion=transaccion, prestamo=prestamo).save()
