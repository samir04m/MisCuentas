from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import pytz
from .models import *
from apps.usuario.models import *

def crearTransaccion(request, tipo:str, cuenta:Cuenta, cantidad:int, info:str, tagName:str, estado:int, fecha=None) -> Transaccion:
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
        etiqueta=getEtiquetaByName(tagName, request.user),
        user=request.user
    )
    transaccion.save()
    return transaccion

def crearPrestamo(request, tipo, cantidad, info, cuenta:Cuenta, persona:Persona, fecha=None) -> Prestamo:
    fecha = validarFecha(fecha)
    if tipo == 'yopresto':
        transaccion = crearTransaccion(request, 'egreso', cuenta, cantidad, info, 'Prestamo', 1, fecha)
    if tipo == 'meprestan':
        transaccion = crearTransaccion(request, 'ingreso', cuenta, cantidad, info, 'Prestamo', 1, fecha)
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
    transaccionPrestamo = TransaccionPrestamo(
        prestamo=prestamo,
        transaccion=transaccion,
        tipo=1
    )
    transaccionPrestamo.save()
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
    if fechaCompra.month+sumarMes > 12:
        month = sumarMes - 1
        year = fechaCompra.year + 1
    else:
        month = fechaCompra.month+sumarMes
        year = fechaCompra.year
    return datetime(year, month, compra.creditCard.diaPago, fechaCompra.hour, fechaCompra.minute, fechaCompra.second)

def getEtiquetaByName(nombre:str, user) -> Etiqueta:
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
    # if request.user.is_superuser:
    #     return Etiqueta.objects.filter(user=request.user)
    # else:
    return Etiqueta.objects.filter(user=request.user, tipo__in=[1,3])

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

def getDate(inputDate:str):
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

def selectCuentas(request, userpersona:UserPersona=None):
    user = userpersona.admin if userpersona else request.user
    return Cuenta.objects.filter(user=user)

def selectEtiquetas(request):
    return Etiqueta.objects.filter(user=request.user, tipo=1)

def getCuentaFromPost(request) -> Cuenta:
    if request.POST.get('cuenta') == '0':
        return None
    else:
        return Cuenta.objects.filter(id=int(request.POST.get('cuenta'))).first()

def getEtiquetaFromPost(request) -> Etiqueta:
    if request.POST.get('tag'):
        return getEtiquetaById(int(request.POST.get('tag')))
    elif request.POST.get('newTag'):
        return getEtiquetaByName(request.POST.get('newTag'), request.user)
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
    def __init__(self, deudaPropia:int, deudaAjena:int):
        self.deudaPropia = deudaPropia
        self.deudaAjena = deudaAjena
        self.deudaTotal = deudaPropia + deudaAjena

def getDeudaTarjetasCredito(request) -> InfoDeudaTarjetasCredito:
    comprasCreditoPropias = CompraCredito.objects.filter(creditCard__user=request.user, etiqueta__tipo=1, cancelada=False).aggregate(Sum('deuda'))
    comprasCreditoAjena = CompraCredito.objects.filter(creditCard__user=request.user, etiqueta__tipo=3, cancelada=False).aggregate(Sum('deuda'))
    deudaPropia = comprasCreditoPropias['deuda__sum'] if comprasCreditoPropias['deuda__sum'] else 0
    deudaAjena = comprasCreditoAjena['deuda__sum'] if comprasCreditoAjena['deuda__sum'] else 0
    return InfoDeudaTarjetasCredito(deudaPropia, deudaAjena)

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

# def agruparTransacciones(request, transaccionNueva):
#     fechaNT = transaccionNueva.fecha.astimezone(pytz.timezone(timezone.get_default_timezone_name())) # convertir la fecha a la zona horaria en la que se guarda en DB

#     transaccionesExistentes = Transaccion.objects.filter(
#         tipo=transaccionNueva.tipo,
#         cuenta=transaccionNueva.cuenta,
#         user=transaccionNueva.user,
#         estado__in=[1,3],
#         fecha__year=fechaNT.year, 
#         fecha__month=fechaNT.month, 
#         fecha__day=fechaNT.day, 
#         fecha__hour=fechaNT.hour,
#         fecha__minute=fechaNT.minute
#     ).exclude(id=transaccionNueva.id)
    
#     if transaccionesExistentes:
#         if len(transaccionesExistentes) > 1:
#             transaccionExistente = transaccionesExistentes.filter(estado=3)
#             print('grupo', transaccionExistente)
#         elif len(transaccionesExistentes) == 1:
#             transaccionExistente = transaccionesExistentes.first()
#         crearGrupoTransaccion(request, transaccionExistente, transaccionNueva)

def crearGrupoTransaccion(request, transaccionPadre:Transaccion, transaccionNueva:Transaccion, fechaTransaccionGrupo = None) -> Transaccion:
    try:
        with transaction.atomic():
            if transaccionPadre.estado == 1:
                # Si la transaccionPadre no esta asignada a un grupo, primero se crea el grupo y se asigna a ese grupo
                nuevaTransaccionPadre = Transaccion(
                    tipo = transaccionPadre.tipo,
                    saldo_anterior = 0,
                    cantidad = transaccionPadre.cantidad,
                    info = '[Grupo] ' + transaccionPadre.info,
                    fecha = fechaTransaccionGrupo if fechaTransaccionGrupo else transaccionPadre.fecha,
                    estado = 3,
                    cuenta = transaccionPadre.cuenta,
                    user = transaccionPadre.user
                )
                nuevaTransaccionPadre.save()
                grupo = GrupoTransaccion(
                    transaccionPadre = nuevaTransaccionPadre,
                    transaccionHija = transaccionPadre
                )
                grupo.save()
                transaccionPadre.estado = 2
                transaccionPadre.save()
                transaccionPadre = nuevaTransaccionPadre # se sobreescribe para que entre en el siguente condicional

            if transaccionPadre.estado == 3:
                grupo = GrupoTransaccion(
                    transaccionPadre = transaccionPadre,
                    transaccionHija = transaccionNueva
                )
                grupo.save()
                transaccionPadre.cantidad += transaccionNueva.cantidad
                transaccionPadre.info += ' - ' + transaccionNueva.info
                transaccionPadre.save()
                transaccionNueva.estado = 2
                transaccionNueva.save()
                return transaccionPadre
    except Exception as ex:
        printException(ex)
        alert(request, 'Ocurrio un error al intentar agrupar las transacciones', 'e')
        return None

def printException(ex):
    line = ex.__traceback__.tb_lineno
    fileName = ex.__traceback__.tb_frame.f_code.co_filename
    print(' | | | | | | | | | | |  Exception | | | | | | | | | | | ')
    print(f" File: {fileName}, line: {line}, Message: {ex}")
    print(' | | | | | | | | | | |  | | | | | | | | | | | | | | | | ')

def alert(request, message:str, type:str='s'):
    if request:
        if type == 's':
            messages.success(request, message)
        elif type == 'e':
            messages.error(request, message)
        elif type == 'i':
            messages.info(request, message)
        elif type == 'w':
            messages.warning(request, message)

def crearEtiquetaPrestamoCompraTC(request):
    etiquetaPrestamoCompraTC = Etiqueta.objects.filter(tipo=3).first()
    if not etiquetaPrestamoCompraTC:
        etiquetaPrestamoCompraTC = Etiqueta(
            nombre = 'Prestamo compra TC',
            tipo=3,
            user=request.user
        )
        etiquetaPrestamoCompraTC.save()