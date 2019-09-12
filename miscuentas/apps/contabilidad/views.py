# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.shortcuts import get_object_or_404
from .forms import *
from .models import *

def home(request):
    return render(request, 'index.html')

def panel(request):
    cuentas = Cuenta.objects.filter(user = request.user)
    personas = Persona.objects.filter(user = request.user)
    context = {'cuentas':cuentas, 'personas':personas}
    return render(request, 'contabilidad/panel.html', context)

def crear_cuenta(request):
    if request.method == 'POST':
        form = CuentaForm(request.POST)
        if form.is_valid():
            cuenta = form.save(commit=False)
            cuenta.user = request.user
            cuenta.save()
            return redirect('panel:panel')
    else:
        form = CuentaForm()

    return render(request, 'contabilidad/crear_cuenta.html', {"form": form})

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

    return render(request, 'contabilidad/crear_persona.html', {"form": form})


def crear_egreso(request, cuenta_id):
    mensaje = None
    # cuenta = Cuenta.objects.get(id=cuenta_id)
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)

    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            egreso = form.save(commit=False)
            if egreso.cantidad <= cuenta.saldo:
                egreso.tipo = 'egreso'
                egreso.cuenta = cuenta

                etiqueta = Etiqueta.objects.get(id=int(request.POST.get('tag')))
                egreso.etiqueta = etiqueta
                egreso.save()
                cuenta.saldo -= egreso.cantidad
                cuenta.save()
                return redirect('panel:panel')
            else:
                form = TransaccionForm(request.POST)
                mensaje = "El valor del egreso no puede superar el valor maximo."
    else:
        form = TransaccionForm()

    tags = Etiqueta.objects.filter(user=request.user.id)
    context = {"form": form, "cuenta":cuenta, "tags":tags, "mensaje":mensaje}
    return render(request, 'contabilidad/crear_egreso.html', context)

def crear_ingreso(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)

    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            ingreso = form.save(commit=False)
            ingreso.tipo = 'ingreso'
            ingreso.cuenta = cuenta
            ingreso.save()
            cuenta.saldo += ingreso.cantidad
            cuenta.save()
            return redirect('panel:panel')
    else:
        form = TransaccionForm()

    context = {"form": form, "cuenta":cuenta}
    return render(request, 'contabilidad/crear_ingreso.html', context)
