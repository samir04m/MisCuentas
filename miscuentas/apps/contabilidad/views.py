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
import math

@login_required
def panel(request):
    cuentas = Cuenta.objects.filter(user = request.user).order_by('id')
    personas = Persona.objects.filter(user = request.user).order_by('id')
    # alert = generateDictFromSessionVariables(request, ['title','text','icon'])
    # context = {'cuentas':cuentas, 'personas':personas, 'alert':alert}
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

            # transaccion = Transaccion(
            #     tipo='ingreso',
            #     saldo_anterior=0,
            #     cantidad=cuenta.saldo,
            #     info='Creación de la cuenta. Definición del saldo inicial.',
            #     cuenta=cuenta,
            #     fecha = datetime.now()
            # )
            # transaccion.save()

            return redirect('panel:panel')
    else:
        form = CuentaForm()

    return render(request, 'contabilidad/cuenta/crear_cuenta.html', {"form": form})

@login_required
def crear_persona(request):
    if request.method == 'POST':
        isCreditCard = True if request.POST.get('isCreditCard') else False
        persona = Persona(
            nombre = request.POST.get('nombre').capitalize(),
            isCreditCard = isCreditCard,
            user = request.user
        )
        persona.save()
        return redirect('panel:panel')

    return render(request, 'contabilidad/persona/crear_persona.html')

@login_required
def vista_persona(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id, user=request.user.id)
    prestamos = Prestamo.objects.filter(persona=persona, cancelada=False)
    yoDebo = 0
    meDeben = 0
    for p in prestamos:
        if p.tipo == 'meprestan': 
            yoDebo += p.saldo_pendiente
        elif p.tipo == 'yopresto':
            meDeben += p.saldo_pendiente

    diferencia = meDeben-yoDebo if (yoDebo > 0 and meDeben > 0) else 0
    diferenciaMensaje = ""
    if diferencia > 0: 
        diferenciaMensaje = "Finalmente a usted le deben"
    elif diferencia < 0:
        diferenciaMensaje = "Finalmente usted debe"
    
    context = {
        "persona": persona, 
        "yoDebo": yoDebo,
        "meDeben": meDeben,
        "diferencia": abs(diferencia),
        "diferenciaMensaje": diferenciaMensaje,
    }
    return render(request, 'contabilidad/persona/vista_persona.html', context)

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
                transaccion.fecha = getDate(request.POST.get('datetime'))
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
            transaccion.fecha = getDate(request.POST.get('datetime'))
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

    tags = Etiqueta.objects.filter(user=request.user.id).exclude(nombre='Prestamo')
    context = {"form": form, "cuenta":cuenta, "tags":tags}
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

    if persona.isCreditCard:
        if request.method == 'POST':
            cantidad = int(request.POST.get('cantidad').replace('.',''))
            info = request.POST.get('info').capitalize()+". " if request.POST.get('info') else ""
            cuotas = int(request.POST.get('cuotas'))
            valorCuotas = (format(math.trunc(cantidad/cuotas), ',d'))
            valorCuotas = valorCuotas.replace(',', '.')
            info += "Diferido a {} cuotas de $ {}".format(cuotas, valorCuotas)

            prestamo = Prestamo(
                tipo = 'meprestan',
                cantidad = cantidad,
                info = info,
                saldo_pendiente = cantidad,
                fecha = getDate(request.POST.get('datetime')),
                persona = persona
            )
            prestamo.save()
            return redirect("panel:vista_persona", persona.id)

        return render(request, 'contabilidad/prestamo/crear_prestamo_tarjeta.html', {"persona":persona})
    else:
        if request.method == 'POST':
            request.POST._mutable = True
            form = PrestamoForm(request.POST)
            form.data['cantidad'] = int(form.data['cantidad'].replace('.',''))

            if form.is_valid():
                prestamo = form.save(commit=False)
                saldo_anterior = 0
                cuenta = None
                if request.POST.get('cuenta') != 'ninguna':
                    cuenta = Cuenta.objects.get(id=int(request.POST.get('cuenta')))
                    if (prestamo.tipo == 'yopresto' and prestamo.cantidad <= cuenta.saldo) or prestamo.tipo == 'meprestan':
                        saldo_anterior = cuenta.saldo
                        prestamo.cuenta = cuenta
                    else:
                        form = PrestamoForm(request.POST)
                        mensaje = "El valor del prestamo no puede superar el saldo en cuenta."

                fecha = getDate(request.POST.get('datetime'))
                prestamo.persona = persona
                prestamo.saldo_pendiente = prestamo.cantidad
                prestamo.fecha = fecha
                prestamo.save()
                if prestamo.tipo == 'yopresto':
                    if cuenta: 
                        cuenta.saldo -= prestamo.cantidad
                    tipoTransaccion = 'egreso'
                    infoTransaccion = 'Le presté a '
                elif prestamo.tipo == 'meprestan':
                    if cuenta: 
                        cuenta.saldo += prestamo.cantidad
                    tipoTransaccion = 'ingreso'
                    infoTransaccion = 'Me prestó '                    

                if cuenta:
                    tag = getEtiqueta('Prestamo', request.user)
                    transaccion = Transaccion(
                        tipo = tipoTransaccion,
                        saldo_anterior = saldo_anterior,
                        cantidad = prestamo.cantidad,
                        info = infoTransaccion + persona.nombre,
                        cuenta = cuenta,
                        etiqueta = tag,
                        fecha = fecha
                    )
                    cuenta.save()
                    transaccion.save()

                return redirect('panel:vista_persona', prestamo.persona.id)                    
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
            infoTransaccion = "Le pagué la totalidad del prestamo a " if prestamo.cancelada else "Le pagué una parte del prestamo a "
            infoTransaccion += prestamo.persona.nombre + ". "
        if cuenta:
            cuenta.save()

        tag = None
        if prestamo.persona.isCreditCard:
            if request.POST.get('tag'):
                tag = Etiqueta.objects.get(id = request.POST.get('tag'))
        else:
            tag = getEtiqueta('Prestamo', request.user)
        print("=========", tag)
        infoAdicional = "\n" + request.POST.get('info') if (request.POST.get('info')) else ""
        transaccion = Transaccion(
            tipo = tipoTransaccion,
            saldo_anterior = saldo_anterior,
            cantidad = monto,
            info = infoTransaccion + infoAdicional,
            cuenta = cuenta,
            etiqueta = tag,
            fecha = getDate(request.POST.get('datetime'))
        )
        transaccion.save()

        transaccionPrestamo = TransaccionPrestamo(transaccion=transaccion, prestamo=prestamo).save()

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

def eliminarTransaccion(transaccion):
    cuenta = transaccion.cuenta
    if cuenta:
        if transaccion.tipo == 'ingreso':
            cuenta.saldo -= transaccion.cantidad
        else:
            cuenta.saldo += transaccion.cantidad
        cuenta.save()
    transaccion.delete()

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
    prestamo.delete()
    messages.success(request, 'Se ha eliminado el prestamo', extra_tags='success')
    return redirect("panel:vista_persona", personaId)

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
    if prestamos:
        saldoTotal = Cuenta.objects.filter(user=request.user).aggregate(Sum('saldo'))
        yoDebo = Prestamo.objects.filter(persona__user=request.user.id, tipo='meprestan', cancelada=False).aggregate(Sum('saldo_pendiente'))
        meDeben = Prestamo.objects.filter(persona__user=request.user.id, tipo='yopresto', cancelada=False).aggregate(Sum('saldo_pendiente'))
        saldoTotal = saldoTotal['saldo__sum']
        yoDebo = yoDebo['saldo_pendiente__sum'] if yoDebo['saldo_pendiente__sum'] else 0
        meDeben = meDeben['saldo_pendiente__sum'] if meDeben['saldo_pendiente__sum'] else 0
        saldoRestante = saldoTotal
        pagandoPrestamosMeQueda = 0
        pagandoPrestamosMensaje = "Saldados todos los prestamos, "
        pagandoPrestamosMeQueda = meDeben-yoDebo    
        if pagandoPrestamosMeQueda >= 0:
            saldoRestante += pagandoPrestamosMeQueda
            pagandoPrestamosMensaje += "usted recuperaria"
        elif pagandoPrestamosMeQueda < 0:
            saldoRestante -= abs(pagandoPrestamosMeQueda)
            pagandoPrestamosMensaje += "usted tendria que pagar"
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
def vista_transaccion(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, id=transaccion_id)
    return render(request, 'contabilidad/transaccion/vista_transaccion.html', {"transaccion":transaccion})

@login_required
def transferir(request, cuenta_id):
    mensaje = None
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, user=request.user.id)
    cuentas_destino = Cuenta.objects.filter(user = request.user.id).exclude(id= cuenta.id)

    if request.method == 'POST':
        egreso = Transaccion( cantidad=int(request.POST.get('cantidad').replace('.','')) )

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
            egreso.save()

            ingreso = Transaccion(
                tipo = 'ingreso',
                cantidad = int(egreso.cantidad),
                saldo_anterior = cuenta_destino.saldo,
                info = 'Transferencia desde ' + cuenta.nombre + info,
                cuenta = cuenta_destino,
                etiqueta = etiqueta,
                fecha = fecha
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
    transaccion = get_object_or_404(Transaccion, id=transaccion_id)
    if request.method == 'POST':
        ok = True
        if transaccion.etiqueta != None and transaccion.etiqueta.nombre == 'Transferencia':
            tipoContrario = 'egreso' if transaccion.tipo == 'ingreso' else 'ingreso'
            transaccion2 = Transaccion.objects.filter(fecha=transaccion.fecha, tipo=tipoContrario, cantidad=transaccion.cantidad).first()
            if transaccion2:
                ok = rollbackTransaction(request, transaccion2)
        elif transaccion.etiqueta != None and transaccion.etiqueta.nombre == 'Prestamo':
            tp = TransaccionPrestamo.objects.filter(transaccion=transaccion).first()
            if tp:
                prestamo = tp.prestamo
                prestamo.saldo_pendiente += transaccion.cantidad
                if prestamo.saldo_pendiente > 0:
                    prestamo.cancelada = False 
                prestamo.save()
                tp.delete()

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
        cuenta = Cuenta.objects.get(id=transaccion.cuenta.id)
        if transaccion.tipo == 'ingreso':
            if cuenta.saldo - transaccion.cantidad >= 0:
                cuenta.saldo = cuenta.saldo - transaccion.cantidad
                sw = True
            else:
                request.session['color'] = "danger"
                request.session['titulo'] = "No es posible deshacer"
                request.session['mensaje'] = "No es posible deshacer la transacción porque el monto actual de la cuenta no lo permite."
                request.session['url'] = "/transaccion/"+str(transaccion.id)
        elif transaccion.tipo == 'egreso':
            cuenta.saldo = cuenta.saldo + transaccion.cantidad
            sw = True
        
        if sw:
            cuenta.save()
            transaccion.delete()
    else:
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

@login_required
def movimientos_dia(request, tipo, fecha):
    date = fecha.split("-")
    day = date[0]
    month = date[1]
    year = date[2]
    fecha2 = datetime(int(year), int(month), int(day))
    tipo2 = 'Egresos' if tipo=='egreso' else 'Ingresos'
    transacciones = Transaccion.objects.filter(cuenta__user=request.user.id, tipo=tipo, fecha__day=day, fecha__month=month, fecha__year=year).exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')

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

def getEtiqueta(nombre, user):
    etiqueta = Etiqueta.objects.filter(nombre=nombre, user=user).first()
    if not etiqueta:
        etiqueta = Etiqueta(nombre=nombre, user=user)
        etiqueta.save()
    return etiqueta

def getDate(inputDate):
    now = datetime.now()
    if inputDate:
        grupos = inputDate.split(" ")
        fecha = grupos[0].split("/")
        hora = grupos[1].split(":")
        hour = getHour24(hora[0], grupos[2])
        date = datetime(int(fecha[2]), int(fecha[1]), int(fecha[0]), hour, int(hora[1]), now.second)
        return date
    else:
        return now

def getHour24(hour, xm):
    if xm == "AM" and hour == "12":
        return 0
    elif xm == "AM":
        return int(hour)
    elif xm == "PM" and hour == "12":
        return int(hour)
    else:
        return int(hour) + 12

def generateDictFromSessionVariables(request, variables):
    dict = {}
    cont = 0
    for var in variables:
        if var in request.session:
            dict[var] = request.session[var]
            del request.session[var]
        else:
            dict[var] = ""
            cont += 1
    if len(variables) == cont:
        dict = None
    return dict

def movimientos_etiqueta_mes(request, etiqueta_id, tipo, periodo):
    etiqueta_id = int(etiqueta_id)
    date = periodo.split("-")
    month = int(date[0])
    year = int(date[1])
    # strTag = ''
    if etiqueta_id > 0:
        tag = Etiqueta.objects.get(id=etiqueta_id)
        strTag = " con etiqueta \"{}\" ".format(tag.nombre)
        transacciones = Transaccion.objects.filter(tipo=tipo, etiqueta=tag, fecha__month=month, fecha__year=year)
    elif etiqueta_id == 0:
        strTag = "sin etiqueta"
        transacciones = Transaccion.objects.filter(tipo=tipo, etiqueta=None, fecha__month=month, fecha__year=year)
    elif etiqueta_id == -1:
        strTag = "del"
        transacciones = Transaccion.objects.filter(tipo=tipo, fecha__month=month, fecha__year=year).exclude(etiqueta__nombre='Prestamo').exclude(etiqueta__nombre='Transferencia')

    strTipo = 'Egresos' if tipo == 'egreso' else 'Ingresos'
    
    context = {
        'tipo': strTipo,
        'etiqueta': strTag,
        'periodo': periodo,
        'transacciones': transacciones,

    }
    return render(request, 'contabilidad/etiqueta/movimientos_etiqueta_mes.html', context)