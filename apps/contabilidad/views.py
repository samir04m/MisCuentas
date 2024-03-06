# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from calendar import month
from multiprocessing import context
from sqlite3 import Timestamp

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, request
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from datetime import datetime
from apps.usuario.models import UserSetting
from apps.usuario.views import getUserSetting, setUserSetting

from .forms import *
from .models import *
from .myFuncs import *
from .viewsPrestamo import *
from .viewsPersona import *
from .viewsEtiqueta import *
from .viewsMovimientos import *
from .viewsCreditCard import *

@login_required
def panel(request):
    cuentas = Cuenta.objects.filter(user = request.user, visible = True).order_by('id')
    personas = Persona.objects.filter(user = request.user, visible = True).order_by('id')
    creditCards = CreditCard.objects.filter(user = request.user, visible = True).order_by('id')
    userpersonas = UserPersona.objects.filter(user = request.user)
    context = {
        "cuentas":cuentas,
        "personas":personas, 
        "creditCards":creditCards,
        "mostrarSaldoCuentas":getUserSetting('MostrarSaldoCuentas', request.user),
        "userpersonas":userpersonas
    }
    return render(request, 'contabilidad/panel.html', context)

@login_required
def crear_cuenta(request):
    if request.method == 'POST':
        request.POST._mutable = True
        form = CuentaForm(request.POST)
        form.data['saldo'] = int(form.data['saldo'].replace('.',''))

        if form.is_valid():
            cuenta = form.save(commit=False)
            cuenta.user = request.user
            cuenta.save()
            messages.success(request, 'Cuenta creada exitosamente', extra_tags='success')
            return redirect('panel:inicio')
    else:
        form = CuentaForm()

    return render(request, 'contabilidad/cuenta/crear_cuenta.html', {"form": form})

@login_required
def crear_egreso(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)

    if request.method == 'POST':
        request.POST._mutable = True
        form = TransaccionForm(request.POST)
        cantidad = getCantidadFromPost(request)
        form.data['cantidad'] = cantidad    # se hace para que pueda pasar la validacion form.is_valid
        if form.is_valid():
            if cantidad <= cuenta.saldo:              
                info = request.POST.get('info')
                fecha = getDate(request.POST.get('datetime'))
                tag = getEtiquetaFromPost(request)
                try:
                    with transaction.atomic():
                        transaccion = crearTransaccion(request, 'egreso', cuenta, cantidad, info, tag, 1, fecha)
                        agregarSubTagFromPost(request, transaccion)
                    messages.success(request, 'Egreso registrado', extra_tags='success')
                except Exception as ex:
                    print("----- Exception -----", ex)
                    messages.error(request, 'Ocurrio un error', extra_tags='error')
                return redirect(request.session['vistaRedireccion'])               
            else:
                form = TransaccionForm(request.POST)
                messages.error(request, 'El valor del egreso no puede superar el saldo de la cuenta.', extra_tags='error')
    else:
        request.session['vistaRedireccion'] = request.META.get('HTTP_REFERER')
        form = TransaccionForm()

    context = {
        "form":form, 
        "cuenta":cuenta, 
        "tags":getSelectEtiquetas(request),
        "mostrarSaldoCuentas":getUserSetting('MostrarSaldoCuentas', request.user)
    }
    return render(request, 'contabilidad/transaccion/crear_egreso.html', context)

@login_required
def crear_ingreso(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)

    if request.method == 'POST':
        request.POST._mutable = True
        form = TransaccionForm(request.POST)
        form.data['cantidad'] = int(form.data['cantidad'].replace('.',''))

        if form.is_valid():
            transaccion = form.save(commit=False)
            transaccion.cantidad = validarMiles(transaccion.cantidad)
            transaccion.tipo = 'ingreso'
            transaccion.cuenta = cuenta
            transaccion.saldo_anterior = cuenta.saldo
            transaccion.fecha = getDate(request.POST.get('datetime'))
            transaccion.user = request.user

            if request.POST.get('newTag'):
                newTag = request.POST.get('newTag')
                if newTag:
                    tag = getEtiquetaByName(newTag, request.user)
                    transaccion.etiqueta = tag
            elif request.POST.get('tag'):
                tag = Etiqueta.objects.get(id=int(request.POST.get('tag')))
                transaccion.etiqueta = tag
            transaccion.save()
            cuenta.saldo += transaccion.cantidad
            cuenta.save()
            messages.success(request, 'Ingreso registrado', extra_tags='success')
            return redirect(request.session['vistaRedireccion'])
    else:
        request.session['vistaRedireccion'] = request.META.get('HTTP_REFERER')
        form = TransaccionForm()

    context = {
        "form":form, 
        "cuenta":cuenta, 
        "tags":getSelectEtiquetas(request),
        "mostrarSaldoCuentas":getUserSetting('MostrarSaldoCuentas', request.user)
    }
    return render(request, 'contabilidad/transaccion/crear_ingreso.html', context)

@login_required
def vista_transaccion(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, id=transaccion_id)
    userpersona = UserPersona.objects.filter(admin=transaccion.user, user=request.user).first()
    if transaccion.user != request.user and not userpersona: # Si el usuario logeado no esta relacionado con la transacción no se permite verla
        raise Http404("Página no encontrada")
    fileName =  'vista_transaccionGrupo.html' if transaccion.estado == 3 else 'vista_transaccion.html'
    request.session['vistaRedireccion'] = request.META.get('HTTP_REFERER')
    transaccionPrestamo = TransaccionPrestamo.objects.filter(transaccion=transaccion, tipo=1).first()
    prestamoRelacionado = transaccionPrestamo.prestamo if transaccionPrestamo else None
    context = {
        "transaccion":transaccion,
        "prestamoRelacionado":prestamoRelacionado,
        "userpersona":userpersona
    }
    return render(request, 'contabilidad/transaccion/'+fileName, context)

@login_required
def transferir(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)
    cuentas_destino = Cuenta.objects.filter(user = request.user.id).exclude(id= cuenta.id)

    if request.method == 'POST':
        egreso = Transaccion( cantidad=int(request.POST.get('cantidad').replace('.','')) )
        egreso.cantidad = validarMiles(egreso.cantidad)
        if egreso.cantidad <= cuenta.saldo:
            fecha = getDate(request.POST.get('datetime'))
            etiqueta = getEtiquetaByName('Transferencia', request.user)
            info = ".\n" + request.POST.get('info') if (request.POST.get('info')) else ""

            cuenta_destino = Cuenta.objects.get(id=int(request.POST.get('cuenta_destino')))
            egreso.info = 'Transferencia a ' + cuenta_destino.nombre + info
            egreso.tipo = 'egreso'
            egreso.cuenta = cuenta
            egreso.saldo_anterior = cuenta.saldo
            egreso.etiqueta = etiqueta
            egreso.fecha = fecha
            egreso.user = request.user
            egreso.save()

            ingreso = Transaccion(
                tipo = 'ingreso',
                cantidad = int(egreso.cantidad),
                saldo_anterior = cuenta_destino.saldo,
                info = 'Transferencia desde ' + cuenta.nombre + info,
                cuenta = cuenta_destino,
                etiqueta = etiqueta,
                fecha = fecha,
                user = request.user
            )
            ingreso.save()

            cuenta.saldo -= egreso.cantidad
            cuenta.save()

            cuenta_destino.saldo += ingreso.cantidad
            cuenta_destino.save()
            return redirect(request.session['vistaRedireccion'])
        else:
            messages.error(request, "El valor de la transferencia no puede superar el valor maximo.", extra_tags='error')
    else:
        request.session['vistaRedireccion'] = request.META.get('HTTP_REFERER')

    context = {
        "cuenta":cuenta, 
        "cuentas_destino":cuentas_destino,
        "mostrarSaldoCuentas":getUserSetting('MostrarSaldoCuentas', request.user)
    }
    return render(request, 'contabilidad/transaccion/transferir.html', context)

@login_required
def transaccion_rollback(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, id=transaccion_id, user=request.user)
    ok = True
    if transaccion.etiqueta != None and transaccion.etiqueta.nombre == 'Transferencia':
        tipoContrario = 'egreso' if transaccion.tipo == 'ingreso' else 'ingreso'
        transaccion2 = Transaccion.objects.filter(fecha=transaccion.fecha, tipo=tipoContrario, cantidad=transaccion.cantidad).first()
        if transaccion2:
            ok = rollbackTransaction(request, transaccion2)
    
    transaccionPrestamo = TransaccionPrestamo.objects.filter(transaccion=transaccion).first()
    if transaccionPrestamo:
        prestamo = transaccionPrestamo.prestamo
        prestamo.saldo_pendiente += transaccion.cantidad
        if prestamo.saldo_pendiente > 0:
            prestamo.cancelada = False 
        prestamo.save()
        transaccionPrestamo.delete()

    if ok:
        ok = rollbackTransaction(request, transaccion)
    if ok:
        messages.success(request, 'Se ha deshecho la transacción', extra_tags='success')
    else:
        messages.error(request, 'No fue posible deshacer la transacción', extra_tags='error')
    return redirect(request.session.get('vistaRedireccion'))

def rollbackTransaction(request, transaccion):
    sw = False
    if transaccion.cuenta:
        cuenta = transaccion.cuenta
        if transaccion.tipo == 'ingreso':
            if cuenta.saldo - transaccion.cantidad >= 0:
                cuenta.saldo = cuenta.saldo - transaccion.cantidad
                sw = True
        elif transaccion.tipo == 'egreso':
            cuenta.saldo = cuenta.saldo + transaccion.cantidad
            sw = True
        
        if sw:
            cuenta.save()
            transaccion.delete()
    else:
        transaccion.delete()
        sw = True
    return sw

@login_required
def crear_transaccion_programada(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                transaccion = Transaccion(
                    tipo = request.POST.get('tipo'),
                    saldo_anterior = 0,
                    cantidad = getCantidadFromPost(request),
                    info = request.POST.get('info'),
                    fecha = getDate(request.POST.get('datetime')),
                    estado = 0,
                    cuenta = getCuentaFromPost(request),
                    etiqueta = getEtiquetaFromPost(request),
                    user = request.user
                )
                transaccion.save()
            messages.success(request, 'Transacción creada', extra_tags='success')
        except Exception as ex:
            print("----- Exception -----", ex)
            messages.error(request, 'Ocurrio un error', extra_tags='error')
        return redirect('panel:transacciones_programadas')        
    else:
        context = {"cuentas":selectCuentas(request), "tags":selectEtiquetas(request)}
        return render(request, 'contabilidad/transaccion/crear_transaccion_programada.html', context)

@login_required
def transacciones_programadas(request):
    programadas = Transaccion.objects.filter(user=request.user, estado=0)
    transacciones = []
    for transaccion in programadas:
        if not transaccion.transaccionpagocredito_set.count():
            transacciones.append(transaccion)
    return render(request, 'contabilidad/transaccion/transacciones_programadas.html', {"transacciones":transacciones})

@login_required
def pagar_transaccion_programada(request, transaccion_id):
    tp = get_object_or_404(Transaccion, id=transaccion_id, user=request.user)
    try:
        with transaction.atomic():
            crearTransaccion(request, tp.tipo, tp.cuenta, tp.cantidad, tp.info, tp.etiqueta, 1)
            tp.delete()
        messages.success(request, 'Se realizó la transacción', extra_tags='success')
    except Exception as ex:
        print("----- Exception -----", ex)
        messages.error(request, 'Ocurrio un error', extra_tags='error')
    return redirect('panel:transacciones_programadas')

@login_required
def agregar_transaccion_grupo(request, transaccionPadre_id):
    transaccionPadre = get_object_or_404(Transaccion, id=transaccionPadre_id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                cantidad = getCantidadFromPost(request)
                info = request.POST.get('info')
                etiqueta = getEtiquetaFromPost(request)
                transaccion = crearTransaccion(request, transaccionPadre.tipo, transaccionPadre.cuenta, cantidad, info, etiqueta, 1)
                agregarSubTagFromPost(request, transaccion)
                nuevaTransaccionPadreGrupo = crearGrupoTransaccion(request, transaccionPadre, transaccion)
            messages.success(request, 'Se agregó la transacción al grupo', extra_tags='success')
            if nuevaTransaccionPadreGrupo:
                return redirect('panel:vista_transaccion', nuevaTransaccionPadreGrupo.id)
        except Exception as ex:
            printException(ex)
            messages.error(request, 'Ocurrio un error', extra_tags='error')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        context = {
            "transaccionPadre":transaccionPadre, 
            "cuenta":Cuenta.objects.get(id=transaccionPadre.cuenta.id),
            "tags":getSelectEtiquetas(request)
        }
        return render(request, 'contabilidad/transaccion/crear_transaccionGrupo.html', context)