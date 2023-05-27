# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from calendar import month
from multiprocessing import context
from sqlite3 import Timestamp

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, request
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from .forms import *
from .models import *
from .myFuncs import *
from .viewsPrestamo import *
from .viewsPersona import *
from .viewsEtiqueta import *
from .viewsMovimientos import *
from .viewsCreditCard import *
import math

@login_required
def panel(request):
    cuentas = Cuenta.objects.filter(user = request.user).order_by('id')
    personas = Persona.objects.filter(user = request.user).order_by('id')
    creditCards = CreditCard.objects.filter(user = request.user).order_by('id')
    context = {
        "cuentas":cuentas,
        "personas":personas, 
        "creditCards":creditCards
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
            return redirect('panel:panel')
    else:
        form = CuentaForm()

    return render(request, 'contabilidad/cuenta/crear_cuenta.html', {"form": form})

@login_required
def crear_egreso(request, cuenta_id):
    mensaje = None
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)

    if request.method == 'POST':
        request.POST._mutable = True
        form = TransaccionForm(request.POST)
        form.data['cantidad'] = int(form.data['cantidad'].replace('.',''))

        if form.is_valid():
            transaccion = form.save(commit=False)
            transaccion.cantidad = validarMiles(transaccion.cantidad)
            if transaccion.cantidad <= cuenta.saldo:
                transaccion.tipo = 'egreso'
                transaccion.cuenta = cuenta
                transaccion.saldo_anterior = cuenta.saldo
                transaccion.fecha = getDate(request.POST.get('datetime'))
                transaccion.user = request.user

                if request.POST.get('newTag'):
                    newTag = request.POST.get('newTag')
                    if newTag:
                        tag = getEtiqueta(newTag, request.user)
                        transaccion.etiqueta = tag
                elif request.POST.get('tag'):
                    tag = Etiqueta.objects.get(id=int(request.POST.get('tag')))
                    transaccion.etiqueta = tag
                transaccion.save()
                cuenta.saldo -= transaccion.cantidad
                cuenta.save()
                messages.success(request, 'Egreso registrado', extra_tags='success')
                return redirect('panel:panel')
            else:
                form = TransaccionForm(request.POST)
                mensaje = "El valor del egreso no puede superar el valor maximo."
    else:
        form = TransaccionForm()

    context = {"form": form, "cuenta":cuenta, "tags":getSelectEtiquetas(request), "mensaje":mensaje}
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
                    tag = getEtiqueta(newTag, request.user)
                    transaccion.etiqueta = tag
            elif request.POST.get('tag'):
                tag = Etiqueta.objects.get(id=int(request.POST.get('tag')))
                transaccion.etiqueta = tag
            transaccion.save()
            cuenta.saldo += transaccion.cantidad
            cuenta.save()
            messages.success(request, 'Ingreso registrado', extra_tags='success')
            return redirect('panel:panel')
    else:
        form = TransaccionForm()

    context = {"form": form, "cuenta":cuenta, "tags":getSelectEtiquetas(request)}
    return render(request, 'contabilidad/transaccion/crear_ingreso.html', context)

@login_required
def vista_transaccion(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, id=transaccion_id, user=request.user)
    return render(request, 'contabilidad/transaccion/vista_transaccion.html', {"transaccion":transaccion})

@login_required
def transferir(request, cuenta_id):
    mensaje = None
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)
    cuentas_destino = Cuenta.objects.filter(user = request.user.id).exclude(id= cuenta.id)

    if request.method == 'POST':
        egreso = Transaccion( cantidad=int(request.POST.get('cantidad').replace('.','')) )
        egreso.cantidad = validarMiles(egreso.cantidad)
        if egreso.cantidad <= cuenta.saldo:
            fecha = getDate(request.POST.get('datetime'))
            etiqueta = getEtiqueta('Transferencia', request.user)
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
            return redirect('panel:panel')
        else:
            mensaje = "El valor de la transferencia no puede superar el valor maximo."

    context = {"cuenta":cuenta, "cuentas_destino":cuentas_destino,  "mensaje":mensaje}
    return render(request, 'contabilidad/transaccion/transferir.html', context)

@login_required
def transaccion_rollback(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, id=transaccion_id, user=request.user)
    if request.method == 'POST':
        ok = True
        if transaccion.etiqueta != None and transaccion.etiqueta.nombre == 'Transferencia':
            tipoContrario = 'egreso' if transaccion.tipo == 'ingreso' else 'ingreso'
            transaccion2 = Transaccion.objects.filter(fecha=transaccion.fecha, tipo=tipoContrario, cantidad=transaccion.cantidad).first()
            if transaccion2:
                ok = rollbackTransaction(request, transaccion2)
        # elif transaccion.etiqueta != None and transaccion.etiqueta.nombre == 'Prestamo':
        #     tp = TransaccionPrestamo.objects.filter(transaccion=transaccion).first()
        #     if tp:
        #         prestamo = tp.prestamo
        #         prestamo.saldo_pendiente += transaccion.cantidad
        #         if prestamo.saldo_pendiente > 0:
        #             prestamo.cancelada = False 
        #         prestamo.save()
        #         tp.delete()
        
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
        return redirect('panel:panel')
    else:
        return render(request, 'contabilidad/transaccion/transaccion_rollback.html', {"transaccion":transaccion})

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
def vista_mensaje(request):
    context = generateDictFromSessionVariables(request, ['titulo','mensaje','url','color'])
    if context:
        return render(request, 'contabilidad/vista_mensaje.html', context)
    else:
        return redirect('panel:panel')

@login_required
def mensaje_confirmacion(request, context):
    return render(request, 'contabilidad/mensaje_confirmacion.html', context)

def confirm_eliminar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    data = {
        "titulo": "Confirmar eliminación de prestamo",
        "mensaje": "¿Esta seguro de eliminar el prestamo?",
        "urlCancel": "/prestamo/"+str(prestamo_id),
        "urlConfirm": "/eliminar-prestamo/"+str(prestamo_id),
        "color": "danger"
    }
    return mensaje_confirmacion(request, data)