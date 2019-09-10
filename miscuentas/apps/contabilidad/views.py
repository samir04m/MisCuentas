# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from .forms import *
from .models import *

def home(request):
    return render(request, 'index.html')

def panel(request):
    cuentas = Cuenta.objects.filter(user = request.user)
    return render(request, 'contabilidad/panel.html', {'cuentas':cuentas})

class CrearCuenta(CreateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'contabilidad/crear_cuenta.html'
    success_url = reverse_lazy('conta:panel')
