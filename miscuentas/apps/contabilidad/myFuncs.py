from django.db.models import Sum
from datetime import datetime
from datetime import timedelta
from .models import *

def crearTransaccion(tipo, cuenta:Cuenta, cantidad, info, tag, estado, user, fecha=None):
    saldo_anterior = 0
    if cuenta:
        saldo_anterior = cuenta.saldo
        if tipo == 'egreso':
            if cuenta.saldo < cantidad:
                raise Exception("No es posible realizar la transacción porque la cuenta no tiene el saldo suficiente")
            else:
                cuenta.saldo = cuenta.saldo - cantidad
        elif tipo == 'ingreso':
            cuenta.saldo = cuenta.saldo + cantidad
        cuenta.save()

    transaccion = Transaccion(
        tipo=tipo,
        saldo_anterior=saldo_anterior,
        cantidad=cantidad,
        info=info,
        fecha=validarFecha(fecha),
        estado=estado,
        cuenta=cuenta,
        etiqueta=getEtiqueta(tag, user),
        user=user
    )
    transaccion.save()
    return transaccion

def crearPrestamo(tipo, cantidad, info, cuenta:Cuenta, persona:Persona, fecha=None):
    fecha = validarFecha(fecha)
    if tipo == 'yopresto':
        crearTransaccion('egreso', cuenta, cantidad, info, 'Prestamo', 1, persona.user, fecha)
    if tipo == 'meprestan':
        crearTransaccion('ingreso', cuenta, cantidad, info, 'Prestamo', 1, persona.user, fecha)
    prestamo = Prestamo(
        tipo=tipo,
        cantidad=cantidad,
        info=info,
        saldo_pendiente=cantidad,
        fecha=fecha,
        cuenta=cuenta,
        persona=persona
    )
    prestamo.save()
    return prestamo

def crearCompraCredito(creditCard:CreditCard, valor:int, cuotas:int, info, etiqueta:Etiqueta, subtag:SubTag, fecha=None):
    compra = CompraCredito(
        creditCard = creditCard,
        etiqueta = etiqueta,
        valor = valor,
        cuotas = cuotas,
        info = info,
        deuda = valor,
        fecha = validarFecha(fecha)
    )
    compra.save()
    creditCard.cupoDisponible = creditCard.cupoDisponible - valor
    creditCard.save()
    crearTransaccionesProgramadas(compra, subtag)
    return compra

def crearTransaccionesProgramadas(compraCredito:CompraCredito, subtag:SubTag):
    for i in range(compraCredito.cuotas):
        nCuota = i+1
        transaccion = Transaccion(
            tipo='egreso',
            saldo_anterior=0,
            cantidad=getValorCuota(compraCredito, nCuota),
            info='{}. Cuota {}.'.format(compraCredito.info, nCuota),
            fecha=getFechaPagoCuota(compraCredito, nCuota),
            estado=0,
            etiqueta=compraCredito.etiqueta,
            subtag=subtag,
            user=compraCredito.creditCard.user
        )
        transaccion.save()
        transaccionCredito = TransaccionPagoCredito(
            compraCredito = compraCredito,
            transaccion = transaccion
        )
        transaccionCredito.save()

def getValorCuota(compraCredito:CompraCredito, nCuota):
    if nCuota == compraCredito.cuotas:
        sumaValorCuotas = round(compraCredito.valor/compraCredito.cuotas) * compraCredito.cuotas
        compensacion = compraCredito.valor - sumaValorCuotas
        return round(compraCredito.valor/compraCredito.cuotas) + compensacion
    else:
        return round(compraCredito.valor/compraCredito.cuotas)

def getFechaPagoCuota(compra:CompraCredito, cuota):
    fechaCompra = compra.fecha
    sumarMes = cuota - 1
    if fechaCompra.day > compra.creditCard.diaCorte:
        sumarMes = sumarMes + 1
    if compra.creditCard.diaPago < compra.creditCard.diaCorte:
        sumarMes = sumarMes + 1
    return datetime(fechaCompra.year, fechaCompra.month+sumarMes, compra.creditCard.diaPago, fechaCompra.hour, fechaCompra.minute, fechaCompra.second)

def getEtiqueta(nombre, user) -> Etiqueta:
    if nombre:
        etiqueta = Etiqueta.objects.filter(nombre=nombre, user=user).first()
        if not etiqueta:
            etiqueta = Etiqueta(nombre=nombre, tipo=getTipoEtiqueta(nombre), user=user)
            etiqueta.save()
        return etiqueta
    return None

def getEtiquetaById(id) -> Etiqueta:
    if id:
        return Etiqueta.objects.get(id=id)
    return None

def getSelectEtiquetas(request):
    if request.user.is_superuser:
        return Etiqueta.objects.filter(user=request.user)
    else:
        return Etiqueta.objects.filter(user=request.user, tipo=1)

def getTipoEtiqueta(nombre) -> int:
    tipo2 = ['Prestamo', 'Transferencia']
    if nombre in tipo2:
        return 2
    else:
        return 1

def eliminarTransaccion(transaccion):
    cuenta = transaccion.cuenta
    if cuenta:
        if transaccion.tipo == 'ingreso':
            cuenta.saldo -= transaccion.cantidad
        else:
            cuenta.saldo += transaccion.cantidad
        cuenta.save()
    transaccion.delete()

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

def validarMiles(cantidad) -> int:
    if len(str(cantidad)) < 4:
        return cantidad * 1000
    else:
        return cantidad

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

def getSaldoTotalCuentas(request):
    cuentas = Cuenta.objects.filter(user=request.user).aggregate(Sum('saldo'))
    return cuentas['saldo__sum'] if cuentas['saldo__sum'] else 0

def getDeudaPrestamos(request):
    prestamosYoDebo = Prestamo.objects.filter(persona__user=request.user, tipo='meprestan', cancelada=False).aggregate(Sum('saldo_pendiente'))
    prestamosMeDeben = Prestamo.objects.filter(persona__user=request.user, tipo='yopresto', cancelada=False).aggregate(Sum('saldo_pendiente'))
    yoDebo = prestamosYoDebo['saldo_pendiente__sum'] if prestamosYoDebo['saldo_pendiente__sum'] else 0
    meDeben = prestamosMeDeben['saldo_pendiente__sum'] if prestamosMeDeben['saldo_pendiente__sum'] else 0
    return DeudaPrestamoData(yoDebo, meDeben)

class DeudaPrestamoData:
    def __init__(self, yoDebo, meDeben):
        self.yoDebo = yoDebo
        self.meDeben = meDeben
        self.deudaTotal = meDeben - yoDebo

def selectCuentas(request):
    return Cuenta.objects.filter(user=request.user)

def selectEtiquetas(request):
    return Etiqueta.objects.filter(user=request.user, tipo=1)

def getCuentaFromPost(request) -> int:
    if request.POST.get('cuenta') == '0':
        return None
    else:
        return Cuenta.objects.get(id=int(request.POST.get('cuenta')))

def getEtiquetaFromPost(request) -> Etiqueta:
    if request.POST.get('tag'):
        return getEtiquetaById(int(request.POST.get('tag')))
    elif request.POST.get('newTag'):
        return getEtiqueta(request.POST.get('newTag'), request.user)
    else:
        return None

def getCantidadFromPost(request) -> int:
    return validarMiles(int(request.POST.get('cantidad').replace('.','')))

def agregarSubTagFromPost(request, transaccion:Transaccion):
    if request.POST.get('subtag'):
        transaccion.subtag = SubTag.objects.get(id=int(request.POST.get('subtag')))
        transaccion.save()

def validarFecha(fecha):
    if fecha:
        return fecha
    else:
        return datetime.now()

class InfoDeudaTarjetasCredito:
    def __init__(self, deudaPropia, deudaPrestamo):
        self.deudaPropia = deudaPropia
        self.deudaPrestamo = deudaPrestamo
        self.deudaTotal = deudaPropia + deudaPrestamo

def getDeudaTarjetasCredito(request) -> InfoDeudaTarjetasCredito:
    comprasCreditoPropias = CompraCredito.objects.filter(creditCard__user=request.user, etiqueta__tipo=1, cancelada=False).aggregate(Sum('deuda'))
    comprasCreditoPrestamo = CompraCredito.objects.filter(creditCard__user=request.user, etiqueta__nombre='Prestamo', cancelada=False).aggregate(Sum('deuda'))
    return InfoDeudaTarjetasCredito(comprasCreditoPropias['deuda__sum'], comprasCreditoPrestamo['deuda__sum'])

def getFormatoDinero(cantidad) -> str:
    if cantidad < 0:
        cantidad *= -1
    strcan = str(cantidad)
    result = []
    cont = 0
    for i in range(len(strcan)-1, -1, -1):
        if cont == 3:
            cont = 0
            result.append(".")
        result.append(strcan[i])
        cont = cont + 1
    result.reverse()
    return "$" + "".join(result)