from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import request
from .models import *
from .forms import *
from .myFuncs import *

@login_required
def todos_movimientos(request):
    transacciones = Transaccion.objects.filter(user=request.user, estado=1)
    return render(request, 'contabilidad/transaccion/todos_movimientos.html', {"transacciones":transacciones})

@login_required
def movimientos_cuenta(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)
    transacciones = Transaccion.objects.filter(cuenta=cuenta.id).order_by('-fecha')
    context =  {"transacciones": transacciones, "cuenta":cuenta}
    return render(request, 'contabilidad/transaccion/movimientos_cuenta.html', context)

@login_required
def movimientos_dia(request, tipo, fecha):
    date = fecha.split("-")
    day = date[0]
    month = date[1]
    year = date[2]
    fecha2 = datetime(int(year), int(month), int(day))
    tipo2 = 'Egresos' if tipo=='egreso' else 'Ingresos'
    transacciones = Transaccion.objects.filter(user=request.user, tipo=tipo, fecha__day=day, fecha__month=month, fecha__year=year).exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')

    context = {'transacciones':transacciones, 'fecha':fecha2, 'tipo':tipo2}
    return render(request, 'contabilidad/transaccion/movimientos_dia.html', context)

@login_required
def movimientos_mes(request, tipo, fecha):
    date = fecha.split("-")
    month = date[0]
    year = date[1]
    fecha2 = datetime(int(year), int(month), 1)
    tipo2 = 'Egresos' if tipo=='egreso' else 'Ingresos'
    transacciones = Transaccion.objects.filter(cuenta__user=request.user.id, tipo=tipo, fecha__month=month, fecha__year=year).exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')

    context = {'transacciones':transacciones, 'fecha':fecha2, 'tipo':tipo2}
    return render(request, 'contabilidad/transaccion/movimientos_mes.html', context)

@login_required
def movimientos_etiqueta(request, etiqueta_id):
    etiqueta = get_object_or_404(Etiqueta, id=etiqueta_id, user=request.user.id)
    transacciones = Transaccion.objects.filter(etiqueta=etiqueta.id, estado=1).order_by('-fecha')

    context =  {"transacciones": transacciones, "etiqueta":etiqueta}
    return render(request, 'contabilidad/etiqueta/movimientos_etiqueta.html', context)

def movimientos_etiqueta_mes(request, etiqueta_id, tipo, periodo):
    etiqueta_id = int(etiqueta_id)
    date = periodo.split("-")
    month = int(date[0])
    year = int(date[1])
    # strTag = ''
    if etiqueta_id > 0:
        tag = Etiqueta.objects.get(id=etiqueta_id)
        strTag = " con etiqueta \"{}\" ".format(tag.nombre)
        transacciones = Transaccion.objects.filter(tipo=tipo, etiqueta=tag, estado=1, fecha__month=month, fecha__year=year)
    elif etiqueta_id == 0:
        strTag = "sin etiqueta"
        transacciones = Transaccion.objects.filter(tipo=tipo, etiqueta=None, estado=1, fecha__month=month, fecha__year=year)
    elif etiqueta_id == -1:
        strTag = "del"
        transacciones = Transaccion.objects.filter(tipo=tipo, estado=1, fecha__month=month, fecha__year=year).exclude(etiqueta__tipo=2)

    strTipo = 'Egresos' if tipo == 'egreso' else 'Ingresos'
    
    context = {
        'tipo': strTipo,
        'etiqueta': strTag,
        'periodo': periodo,
        'transacciones': transacciones,

    }
    return render(request, 'contabilidad/etiqueta/movimientos_etiqueta_mes.html', context)