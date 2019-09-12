# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
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
    tags = None
    cuenta = Cuenta.objects.get(id=cuenta_id)

    if request.method == 'POST':
        #validar Cantidad

        form = EgresoForm(request.POST)
        if form.is_valid():
            egreso = form.save(commit=False)
            egreso.tipo = 'egreso'
            egreso.cuenta = cuenta

            etiqueta = Etiqueta.objects.get(id=int(request.POST.get('tag')))
            egreso.etiqueta = etiqueta
            egreso.save()
            return redirect('panel:panel')
    else:
        form = EgresoForm()
        tags = Etiqueta.objects.filter(user=request.user.id)

    context = {"form": form, "cuenta":cuenta, "tags":tags}
    return render(request, 'contabilidad/crear_egreso.html', context)
