# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, request
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *

@login_required
def panel(request):
    cuentas = Cuenta.objects.filter(user = request.user)
    personas = Persona.objects.filter(user = request.user)
    context = {'cuentas':cuentas, 'personas':personas}
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

            transaccion = Transaccion(
                tipo='ingreso',
                saldo_anterior=0,
                cantidad=cuenta.saldo,
                info='Creación de la cuenta. Definición del saldo inicial.',
                cuenta=cuenta
            ).save()

            return redirect('panel:panel')
    else:
        form = CuentaForm()

    return render(request, 'contabilidad/cuenta/crear_cuenta.html', {"form": form})

@login_required
def crear_persona(request):
    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            persona = form.save(commit=False)
            persona.user = request.user
            persona.save()
            return redirect('panel:panel')
    else:
        form = PersonaForm()

    return render(request, 'contabilidad/persona/crear_persona.html', {"form": form})

@login_required
def vista_persona(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id, user=request.user.id)
    return render(request, 'contabilidad/persona/vista_persona.html', {"persona":persona})

@login_required
def crear_egreso(request, cuenta_id):
    mensaje = None
    # cuenta = Cuenta.objects.get(id=cuenta_id)
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)

    if request.method == 'POST':
        request.POST._mutable = True
        form = TransaccionForm(request.POST)
        form.data['cantidad'] = int(form.data['cantidad'].replace('.',''))

        if form.is_valid():
            transaccion = form.save(commit=False)
            if transaccion.cantidad <= cuenta.saldo:
                transaccion.tipo = 'egreso'
                transaccion.cuenta = cuenta
                transaccion.saldo_anterior = cuenta.saldo
                if request.POST.get('tag'):
                    tag = Etiqueta.objects.get(id=int(request.POST.get('tag')))
                    transaccion.etiqueta = tag
                transaccion.save()
                cuenta.saldo -= transaccion.cantidad
                cuenta.save()
                return redirect('panel:panel')
            else:
                form = TransaccionForm(request.POST)
                mensaje = "El valor del egreso no puede superar el valor maximo."
    else:
        form = TransaccionForm()

    tags = Etiqueta.objects.filter(user=request.user.id).exclude(nombre='Prestamo').exclude(nombre='Transferencia')
    context = {"form": form, "cuenta":cuenta, "tags":tags, "mensaje":mensaje}
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
            transaccion.tipo = 'ingreso'
            transaccion.cuenta = cuenta
            transaccion.saldo_anterior = cuenta.saldo
            transaccion.save()
            cuenta.saldo += transaccion.cantidad
            cuenta.save()
            return redirect('panel:panel')
    else:
        form = TransaccionForm()

    context = {"form": form, "cuenta":cuenta}
    return render(request, 'contabilidad/transaccion/crear_ingreso.html', context)

@login_required
def movimientos_cuenta(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)
    transacciones = Transaccion.objects.filter(cuenta=cuenta.id).order_by('-fecha')
    context =  {"transacciones": transacciones, "cuenta":cuenta}
    return render(request, 'contabilidad/transaccion/movimientos_cuenta.html', context)

@login_required
def todos_movimientos(request):
    transacciones = Transaccion.objects.filter(cuenta__user = request.user.id)
    return render(request, 'contabilidad/transaccion/todos_movimientos.html', {"transacciones":transacciones})

@login_required
def movimientos_etiqueta(request, etiqueta_id):
    etiqueta = get_object_or_404(Etiqueta, id=etiqueta_id, user=request.user.id)
    transacciones = Transaccion.objects.filter(etiqueta=etiqueta.id).order_by('-fecha')

    context =  {"transacciones": transacciones, "etiqueta":etiqueta}
    return render(request, 'contabilidad/etiqueta/movimientos_etiqueta.html', context)

@login_required
def crear_etiqueta(request):
    if request.method == 'POST':
        form = EtiquetaForm(request.POST)
        if form.is_valid():
            etiqueta = form.save(commit=False)
            etiqueta.user = request.user
            etiqueta.save()
            return redirect('panel:listar_etiquetas')
    else:
        form = EtiquetaForm()

    return render(request, 'contabilidad/etiqueta/crear_etiqueta.html', {"form": form})

@login_required
def listar_etiquetas(request):
    etiquetas = Etiqueta.objects.filter(user = request.user.id).order_by('nombre')
    return render(request, 'contabilidad/etiqueta/listar_etiquetas.html', {"etiquetas":etiquetas})

class EditarEtiqueta(UpdateView):
    model = Etiqueta
    form_class = EtiquetaForm
    template_name = 'contabilidad/etiqueta/crear_etiqueta.html'
    success_url = reverse_lazy('panel:listar_etiquetas')

class EliminarEtiqueta(DeleteView):
    model = Etiqueta
    template_name = 'contabilidad/etiqueta/etiqueta_confirm_delete.html'
    success_url = reverse_lazy('panel:listar_etiquetas')

@login_required
def crear_prestamo(request, persona_id):
    mensaje = None
    persona = get_object_or_404(Persona, id=persona_id, user=request.user.id)

    if request.method == 'POST':
        request.POST._mutable = True
        form = PrestamoForm(request.POST)
        form.data['cantidad'] = int(form.data['cantidad'].replace('.',''))

        if form.is_valid():
            prestamo = form.save(commit=False)
            cuenta = Cuenta.objects.get(id=int(request.POST.get('cuenta')))

            if (prestamo.tipo == 'yopresto' and prestamo.cantidad <= cuenta.saldo) or prestamo.tipo == 'meprestan':
                prestamo.cuenta = cuenta
                prestamo.persona = persona
                prestamo.saldo_pendiente = prestamo.cantidad
                prestamo.save()
                if prestamo.tipo == 'yopresto':
                    cuenta.saldo -= prestamo.cantidad
                    tipoTransaccion = 'egreso'
                    infoTransaccion = 'Le presté a '
                elif prestamo.tipo == 'meprestan':
                    cuenta.saldo += prestamo.cantidad
                    tipoTransaccion = 'ingreso'
                    infoTransaccion = 'Me prestó '
                cuenta.save()

                tag = getEtiqueta('Prestamo', request.user)
                transaccion = Transaccion(
                    tipo = tipoTransaccion,
                    saldo_anterior = cuenta.saldo,
                    cantidad = prestamo.cantidad,
                    info = infoTransaccion + persona.nombre,
                    cuenta = cuenta,
                    etiqueta = tag
                ).save()

                return redirect('panel:vista_persona', prestamo.persona.id)
            else:
                form = PrestamoForm(request.POST)
                mensaje = "El valor del prestamo no puede superar el saldo en cuenta."
    else:
        form = PrestamoForm()

    cuentas = Cuenta.objects.filter(user=request.user.id)
    context = {"form": form, "cuentas":cuentas, "persona":persona, "mensaje":mensaje}
    return render(request, 'contabilidad/prestamo/crear_prestamo.html', context)

@login_required
def vista_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    return render(request, 'contabilidad/prestamo/vista_prestamo.html', {"prestamo":prestamo})

@login_required
def pagar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)

    if request.method == 'POST':
        monto = int(request.POST.get('monto').replace('.',''))
        if monto > prestamo.saldo_pendiente: 
            monto = prestamo.saldo_pendiente

        cuenta = Cuenta.objects.get(id = request.POST.get('cuenta'))
        if cuenta:
            prestamo.saldo_pendiente -= monto
            if prestamo.saldo_pendiente == 0:
                prestamo.cancelada = True
            prestamo.save()

            saldo_anterior = cuenta.saldo
            if prestamo.tipo == 'yopresto':
                cuenta.saldo += monto
                tipoTransaccion = 'ingreso'
                infoTransaccion = " pagó la totalidad del prestamo." if prestamo.cancelada else " pagó una parte del prestamo."
                infoTransaccion = prestamo.persona.nombre + infoTransaccion
            elif prestamo.tipo == 'meprestan':
                cuenta.saldo -= monto
                tipoTransaccion = 'egreso'
                infoTransaccion = "Le pagué la totalidad del prestamo a " if prestamo.cancelada else "Le pagué una parte del prestamo a "
                infoTransaccion += prestamo.persona.nombre
            cuenta.save()

            tag = getEtiqueta('Prestamo', request.user)
            transaccion = Transaccion(
                tipo = tipoTransaccion,
                saldo_anterior = saldo_anterior,
                cantidad = monto,
                info = infoTransaccion,
                cuenta = cuenta,
                etiqueta = tag
            )
            transaccion.save()

            transaccionPrestamo = TransaccionPrestamo(transaccion=transaccion, prestamo=prestamo).save()

        return redirect('panel:vista_prestamo', prestamo_id)
    else:
        cuentas = Cuenta.objects.filter(user=request.user)
        context = {"cuentas": cuentas, "saldo_pendiente": prestamo.saldo_pendiente}
        return render(request, 'contabilidad/prestamo/pagar_prestamo.html', context)


@login_required
def listar_personas(request):
    personas = Persona.objects.filter(user = request.user.id)
    return render(request, 'contabilidad/persona/listar_personas.html', {"personas":personas})

class EditarPersona(UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'contabilidad/persona/crear_persona.html'
    success_url = reverse_lazy('panel:listar_personas')

class EliminarPersona(DeleteView):
    model = Persona
    template_name = 'contabilidad/persona/persona_confirm_delete.html'
    success_url = reverse_lazy('panel:listar_personas')

@login_required
def listar_prestamos(request):
    prestamos = Prestamo.objects.filter(persona__user = request.user.id)
    return render(request, 'contabilidad/prestamo/listar_prestamos.html', {'prestamos':prestamos})

@login_required
def vista_transaccion(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, id=transaccion_id, cuenta__user=request.user.id)
    return render(request, 'contabilidad/transaccion/vista_transaccion.html', {"transaccion":transaccion})

@login_required
def transferir(request, cuenta_id):
    mensaje = None
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)
    cuentas_destino = Cuenta.objects.filter(user = request.user.id).exclude(id= cuenta.id)

    if request.method == 'POST':
        egreso = Transaccion( cantidad=int(request.POST.get('cantidad').replace('.','')) )

        if egreso.cantidad <= cuenta.saldo:
            etiqueta = getEtiqueta('Transferencia', request.user)

            cuenta_destino = Cuenta.objects.get(id=int(request.POST.get('cuenta_destino')))
            egreso.info = 'Transferencia a '+cuenta_destino.nombre
            egreso.tipo = 'egreso'
            egreso.cuenta = cuenta
            egreso.saldo_anterior = cuenta.saldo
            egreso.etiqueta = etiqueta
            egreso.save()

            ingreso = Transaccion(
                tipo = 'ingreso',
                cantidad = int(egreso.cantidad),
                saldo_anterior = cuenta_destino.saldo,
                info = 'Transferencia desde '+cuenta.nombre,
                cuenta = cuenta_destino,
                etiqueta = etiqueta
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

def getEtiqueta(nombre, user):
    etiqueta = Etiqueta.objects.filter(nombre=nombre).first()
    if not etiqueta:
        etiqueta = Etiqueta(nombre=nombre, user=user).save()
        # print(vars(etiqueta))
    return etiqueta