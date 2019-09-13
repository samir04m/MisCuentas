# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
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


def movimientos_cuenta(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)
    transaciones = Transaccion.objects.filter(cuenta=cuenta.id).order_by('-fecha')

    paginator = Paginator(transaciones, 20)
    page = request.GET.get('page')
    transaciones = paginator.get_page(page)
    context =  {"transaciones": transaciones, "cuenta":cuenta}
    return render(request, 'contabilidad/movimientos_cuenta.html', context)

def todos_movimientos(request):
    transaciones = Transaccion.objects.filter(cuenta__user = request.user.id).order_by('-fecha')

    paginator = Paginator(transaciones, 20)
    page = request.GET.get('page')
    transaciones = paginator.get_page(page)
    return render(request, 'contabilidad/todos_movimientos.html', {"transaciones":transaciones})

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

    return render(request, 'contabilidad/crear_etiqueta.html', {"form": form})

def listar_etiquetas(request):
    etiquetas = Etiqueta.objects.filter(user = request.user.id).order_by('-nombre')
    return render(request, 'contabilidad/listar_etiquetas.html', {"etiquetas":etiquetas})

class EditarEtiqueta(UpdateView):
    model = Etiqueta
    form_class = EtiquetaForm
    template_name = 'contabilidad/crear_etiqueta.html'
    success_url = reverse_lazy('panel:listar_etiquetas')

class EliminarEtiqueta(DeleteView):
    model = Etiqueta
    success_url = reverse_lazy('panel:listar_etiquetas')
