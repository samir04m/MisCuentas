from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import request
from django.db import transaction
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
                alert(request, 'Tarjeta de crédito creada')
            except Exception as ex:
                print("----- Exception -----", ex)
                alert(request, 'No fue posible crear la tarjeta debido a un error', 'e')
            return redirect('panel:inicio')
    else:
        form = CreditCardForm()

    return render(request, 'contabilidad/creditCard/crear_creditCard.html', {"form": form})

@login_required
def vista_creditCard(request, creditCard_id):
    creditCard = get_object_or_404(CreditCard, id=creditCard_id, user=request.user) 
    cuentas = Cuenta.objects.filter(user=request.user)
    deudaPropia = CompraCredito.objects.filter(creditCard=creditCard, etiqueta__tipo=1, cancelada=False).aggregate(Sum('deuda'))
    deudaAjena = CompraCredito.objects.filter(creditCard=creditCard, etiqueta__tipo=3, cancelada=False).aggregate(Sum('deuda'))    
    context = {
        "creditCard": creditCard,
        "cuentas": cuentas,
        "deudaMes": getPagoMes(creditCard),
        "proximosPagos": getProximosPagos(creditCard),
        "deudaPropia": int(deudaPropia['deuda__sum']) if deudaPropia['deuda__sum'] else 0,
        "deudaAjena": int(deudaAjena['deuda__sum']) if deudaAjena['deuda__sum'] else 0
    }
    return render(request, 'contabilidad/creditCard/vista_creditCard.html', context)

@login_required
def listar_creditCards(request):
    creditcards = CreditCard.objects.filter(user=request.user, visible=True)
    context = { 'creditcards': creditcards, 'infoDeuda':getDeudaTarjetasCredito(request) }
    return render(request, 'contabilidad/creditCard/listar_creditCards.html', context)


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
            alert(request, 'La deuda a pagar debe ser mayor a cero', 'e')
        elif cuenta.saldo < deudaAPagar:
            alert(request, 'La cuenta seleccionada no tiene el saldo suficiente para pagar la deuda', 'e')
        else:
            try:
                pagarDeuda(request, creditCard, cuenta, tipoPago)
                alert(request, 'Pago realizado')
            except Exception as ex:
                print("----- Exception -----", ex)
                alert(request, 'Ocurrió un error al realizar el pago', 'e')
    return redirect('panel:vista_creditCard', tarjeta_id)

# import traceback

@login_required
def crear_compra(request, creditCard_id):
    creditCard = get_object_or_404(CreditCard, id=creditCard_id, user=request.user)
    if request.method == 'POST':
        valor = getCantidadFromPost(request)
        cuotas = int(request.POST.get('cuotas'))
        info = request.POST.get('info')
        fecha = getDate(request.POST.get('datetime'))
        personas = request.POST.getlist('personas')
        if personas:
            etiqueta = Etiqueta.objects.filter(tipo=3).first()
        else:
            etiqueta = getEtiquetaFromPost(request)
        if request.POST.get('subtag'):
            subtag = SubTag.objects.get(id=int(request.POST.get('subtag')))
        else:
            subtag = None
        try:
            with transaction.atomic():
                compra = crearCompraCredito(creditCard, valor, cuotas, info, etiqueta, subtag, fecha)
                crearPrestamoCompraTC(compra, personas)
            alert(request, 'Compra registrada')
        except Exception as ex:
            print("----- Exception -----", ex)
            # print("----- Exception -----",traceback.format_exc())
            alert(request, 'No fue posible registrar la compra', 'e')
        return redirect('panel:vista_creditCard', creditCard.id)
    else:
        crearEtiquetaPrestamoCompraTC(request)
        context = {
            "creditCard": creditCard, 
            "tags": getSelectEtiquetas(request), 
            "personas": Persona.objects.filter(user=request.user, visible=True)
        }
        return render(request, 'contabilidad/creditCard/compra_creditCard.html', context)

@login_required
def vista_compra(request, compra_id):
    compra = get_object_or_404(CompraCredito, id=compra_id)
    return render(request, 'contabilidad/creditCard/vista_compraCredito.html', {"compra":compra})

@login_required
def eliminar_compra(request, compra_id):
    compra = get_object_or_404(CompraCredito, id=compra_id)
    creditCard = compra.creditCard
    try:
        with transaction.atomic():
            for transaccionCompra in compra.transaccionpagocredito_set.all():
                transaccion = transaccionCompra.transaccion
                transaccion.delete()
                transaccionCompra.delete()
            for compraPrestamo in compra.compracreditoprestamo_set.all():
                prestamo = compraPrestamo.prestamo
                prestamo.delete() # con la eliminacion en cascade se borra el registro compraCreditoPrestamo
            creditCard.cupoDisponible += compra.valor
            creditCard.save()
            compra.delete()
        alert(request, 'Compra eliminada')
    except Exception as ex:
        print("----- Exception -----", ex)
        alert(request, 'Ocurrio un error', 'e')

    return redirect('panel:vista_creditCard', creditCard.id)

def pagarDeuda(request, creditCard:CreditCard, cuenta:Cuenta, tipoPago:int):
    comprasPendientes = CompraCredito.objects.filter(creditCard=creditCard, cancelada=False)
    transaccionPadre = None
    for compra in comprasPendientes:
        cuotasCanceladas = 0
        for transaccionCompra in compra.transaccionpagocredito_set.all():
            transaccion = transaccionCompra.transaccion
            transaccionNueva = None
            if transaccion.estado == 0:
                if tipoPago == 1: # Totalidad deuda
                    transaccionNueva = realizarPagoTransaccion(transaccion, cuenta, compra)
                    compra.deuda -= transaccion.cantidad
                    creditCard.cupoDisponible += transaccion.cantidad
                    cuotasCanceladas += 1
                elif tipoPago == 2: # Solo pagar correspondientes al mes actual
                    fecha = datetime.now()
                    if transaccion.fecha.year == fecha.year and transaccion.fecha.month == fecha.month:
                        transaccionNueva = realizarPagoTransaccion(transaccion, cuenta, compra)
                        compra.deuda -= transaccion.cantidad
                        creditCard.cupoDisponible += transaccion.cantidad
                        cuotasCanceladas += 1
                if transaccionNueva: # logica para agrupar las transacciones que se van realizando
                    if transaccionPadre:
                        transaccionPadre = crearGrupoTransaccion(None, transaccionPadre, transaccionNueva, getDate(request.POST.get('datetime')))
                    else:
                        transaccionPadre = transaccionNueva # Solo se iguala la primera vez
            elif transaccion.estado == 1:
                cuotasCanceladas += 1
        if cuotasCanceladas == compra.transaccionpagocredito_set.count():
            compra.cancelada = True
        if cuotasCanceladas > 0:
            compra.save()
            creditCard.save()

def realizarPagoTransaccion(transaccion:Transaccion, cuenta:Cuenta, compra:CompraCredito) -> Transaccion:
    transaccion.saldo_anterior = cuenta.saldo
    cuenta.saldo = cuenta.saldo - transaccion.cantidad
    transaccion.cuenta = cuenta
    # transaccion.fecha = datetime.now()
    transaccion.fecha = compra.fecha
    transaccion.estado = 1
    cuenta.save()
    transaccion.save()
    return transaccion

def getPagoMes(creditCard:CreditCard, fecha=None):
    if not fecha:
        fecha = datetime.now()
    comprasPendientes = CompraCredito.objects.filter(creditCard=creditCard, cancelada=False)
    sumaDeuda = 0
    for compra in comprasPendientes:
        for transaccionCompra in compra.transaccionpagocredito_set.all():
            transaccion = transaccionCompra.transaccion
            if transaccion.fecha.year == fecha.year and transaccion.fecha.month == fecha.month:
                if transaccion.estado == 0:
                    sumaDeuda += transaccion.cantidad
    return sumaDeuda

class PagoMes:
    def __init__(self, fecha:str, pagoMes:int):
        self.fecha = fecha
        self.pagoMes = pagoMes    

def getProximosPagos(creditCard:CreditCard):
    fecha = datetime.now()
    month = int(fecha.month)
    year = int(fecha.year)
    proximosPagos = []
    for i in range(24):
        month += 1
        if month == 13:
            month = 1
            year += 1
        fechaConsulta = datetime(year, month, creditCard.diaPago)
        pagoMes = getPagoMes(creditCard, fechaConsulta)
        if pagoMes > 0 :
            item = PagoMes(fechaConsulta.strftime("%d/%m/%Y"), pagoMes)
            proximosPagos.append(item)
        else:
            break
    return proximosPagos

def crearPrestamoCompraTC(compra:CompraCredito, personasIds):
    if personasIds:
        personas = Persona.objects.filter(id__in=personasIds)
        valorPorPersona = int(compra.valor/len(personas))
        info = 'Compra con tarjeta de crédito: ' + compra.info
        try:
            with transaction.atomic():
                for persona in personas:
                    prestamo = Prestamo(
                        tipo='yopresto',
                        cantidad=valorPorPersona,
                        info=info,
                        saldo_pendiente=valorPorPersona,
                        fecha=datetime.now(),
                        cuenta=None,
                        persona=persona
                    )
                    prestamo.save()
                    compraPrestamo = CompraCreditoPrestamo(
                        compraCredito=compra,
                        prestamo=prestamo
                    )
                    compraPrestamo.save()
        except Exception as ex:
            printException(ex)