from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import request
from .models import *
from .forms import *
from .myFuncs import *

@login_required
def crear_creditCard(request):
    if request.method == 'POST':
        request.POST._mutable = True
        form = CreditCardForm(request.POST)
        form.data['cupo'] = int(form.data['cupo'].replace('.',''))
        if form.is_valid():
            creditCard = form.save(commit=False)
            creditCard.cupoDisponible = creditCard.cupo
            creditCard.user = request.user
            try:
                creditCard.save()
                messages.success(request, 'Tarjeta de crédito creada', extra_tags='success')
            except Exception as ex:
                print("----- Exception -----", ex)
                messages.error(request, 'No fue posible crear la tarjeta debido a un error', extra_tags='error')
            return redirect('panel:panel')
    else:
        form = CreditCardForm()

    return render(request, 'contabilidad/creditCard/crear_creditCard.html', {"form": form})

@login_required
def vista_creditCard(request, creditCard_id):
    creditCard = get_object_or_404(CreditCard, id=creditCard_id, user=request.user)
    deudaTotal = creditCard.cupo - creditCard.cupoDisponible
    cuentas = Cuenta.objects.filter(user=request.user)
    context = {
        "creditCard": creditCard,
        "deudaTotal": deudaTotal,
        "cuentas": cuentas,
        "deudaMes": getPagoMes(creditCard)
    }
    return render(request, 'contabilidad/creditCard/vista_creditCard.html', context)

@login_required
def compra_creditCard(request, creditCard_id):
    creditCard = get_object_or_404(CreditCard, id=creditCard_id, user=request.user)
    if request.method == 'POST':
        valor = validarMiles(int(request.POST.get('valor').replace('.','')))
        cuotas = int(request.POST.get('cuotas'))
        info = request.POST.get('info')
        fecha = getDate(request.POST.get('datetime'))
        etiquetaId = request.POST.get('tag')
        if request.POST.get('newTag'):
            nuevaEtiqueta = getEtiqueta(request.POST.get('newTag'), request.user)
            etiquetaId = nuevaEtiqueta.id
        
        try:
            compra = crearCompraCredito(creditCard, etiquetaId, valor, cuotas, info, fecha)
            messages.success(request, 'Compra registrada', extra_tags='success')
        except Exception as ex:
            print("----- Exception -----", ex)
            messages.error(request, 'No fue posible registrar la compra', extra_tags='error')
        return redirect('panel:vista_creditCard', creditCard.id)
    else:
        context = {"creditCard": creditCard, "tags":getSelectEtiquetas(request)}
        return render(request, 'contabilidad/creditCard/compra_creditCard.html', context)

@login_required
def vista_compra(request, compra_id):
    compra = get_object_or_404(CompraCredito, id=compra_id)        
    return render(request, 'contabilidad/creditCard/vista_compraCredito.html', {"compra":compra})

@login_required
def pagar_tarjeta(request, tarjeta_id):
    creditCard = get_object_or_404(CreditCard, id=tarjeta_id)
    if request.method == 'POST':
        cuenta = Cuenta.objects.get( id = int(request.POST.get('cuenta')) )
        tipoPago = int(request.POST.get('tipoPago'))
        if tipoPago == 1:
            deudaAPagar = int(request.POST.get('deudaTotal'))
        elif tipoPago == 2:
            deudaAPagar = int(request.POST.get('deudaMes'))
        if deudaAPagar <= 0:
            messages.error(request, 'La deuda a pagar debe ser mayor a cero', extra_tags='error')
        elif cuenta.saldo < deudaAPagar:
            messages.error(request, 'La cuenta seleccionada no tiene el saldo suficiente para pagar la deuda', extra_tags='error')
        else:
            try:
                pagarDeuda(creditCard, cuenta, tipoPago)
                messages.success(request, 'Pago realizado', extra_tags='success')
            except Exception as ex:
                print("----- Exception -----", ex)
                messages.error(request, 'Ocurrió un error al realizar el pago', extra_tags='error')
    return redirect('panel:vista_creditCard', tarjeta_id)

def pagarDeuda(creditCard:CreditCard, cuenta:Cuenta, tipoPago:int):
    comprasPendientes = CompraCredito.objects.filter(creditCard=creditCard, cancelada=False)
    for compra in comprasPendientes:
        cuotasCanceladas = 0
        for transaccionCompra in compra.transaccionpagocredito_set.all():
            transaccion = transaccionCompra.transaccion
            if transaccion.estado == 0:
                if tipoPago == 1: # Totalidad deuda
                    realizarPagoTransaccion(transaccion, cuenta)
                    compra.deuda -= transaccion.cantidad
                    creditCard.cupoDisponible += transaccion.cantidad
                    cuotasCanceladas += 1
                elif tipoPago == 2: # Solo pagar correspondientes al mes actual
                    fecha = datetime.now()
                    if transaccion.fecha.year == fecha.year and transaccion.fecha.month == fecha.month:
                        realizarPagoTransaccion(transaccion, cuenta)
                        compra.deuda -= transaccion.cantidad
                        creditCard.cupoDisponible += transaccion.cantidad
                        cuotasCanceladas += 1
            elif transaccion.estado == 1:
                cuotasCanceladas += 1
        if cuotasCanceladas == compra.transaccionpagocredito_set.count():
            compra.cancelada = True
        if cuotasCanceladas > 0:
            compra.save()
            creditCard.save()

def realizarPagoTransaccion(transaccion:Transaccion, cuenta:Cuenta):
    transaccion.saldo_anterior = cuenta.saldo
    cuenta.saldo = cuenta.saldo - transaccion.cantidad
    transaccion.cuenta = cuenta
    transaccion.fecha = datetime.now()
    transaccion.estado = 1
    cuenta.save()
    transaccion.save()

def getPagoMes(creditCard:CreditCard):
    comprasPendientes = CompraCredito.objects.filter(creditCard=creditCard, cancelada=False)
    sumaDeuda = 0
    for compra in comprasPendientes:
        for transaccionCompra in compra.transaccionpagocredito_set.all():
            transaccion = transaccionCompra.transaccion
            fecha = datetime.now()
            if transaccion.fecha.year == fecha.year and transaccion.fecha.month == fecha.month:
                if transaccion.estado == 0:
                    sumaDeuda += transaccion.cantidad
    return sumaDeuda
    