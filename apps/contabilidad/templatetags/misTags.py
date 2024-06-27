from django import template
from datetime import datetime
from apps.contabilidad.models import Transaccion
from apps.reporte.myFuncs import TagData
from typing import List
import copy

register = template.Library()

@register.filter
def puntomil(cantidad:int):
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
    cadena = "".join(result)
    return cadena

@register.filter
def textcolor(transaccion:Transaccion):
    if transaccion.estado == 0:
        return 'text-secondary'
    if transaccion.tipo == 'ingreso': 
        return 'text-primary'
    elif transaccion.tipo == 'egreso': 
        return 'text-danger'

@register.filter
def signo(tipo):
    if tipo == 'ingreso': return '+'
    elif tipo == 'egreso': return '-'

@register.filter
def cancelada_icono(cancelada):
    if cancelada: return 'far fa-check-circle text-success'
    else: return 'far fa-times-circle text-danger'

@register.filter
def cancelada_color(cancelada):
    if cancelada: return 'text-secondary'
    else: return 'text-primary'

@register.filter
def sin_etiqueta(transaccion):
    if not transaccion.etiqueta:
        return "-"
    else: 
        return transaccion.etiqueta

@register.filter
def invertir(querySet):
    return querySet.reverse()

@register.filter
def getMessage(messages, field = 'message'):
    for msg in messages:
        if field == 'message':
            return msg.message
        elif field == 'icon':
            return msg.extra_tags

@register.filter
def tableClass(tagName, type):
    if tagName == 'Total periodo':
        if type == 'egreso':
            return 'class=table-danger'
        elif type == 'ingreso':
            return 'class=table-primary'
    return ""

@register.filter
def estadoTransaccion(estado):
    if estado == 0:
        return 'Pediente de pago'
    elif estado == 1:
        return 'Pago realizado'
    else:
        return ''

@register.filter
def colorEstadoTransaccion(estado):
    if estado == 1:
        return 'table-secondary'
    return ''

@register.filter
def operacion(valor1:int, valor2:int, operacion):
    if operacion == '+':
        return valor1 + valor2
    elif operacion == '-':
        return valor1 - valor2
    elif operacion == '*':
        return valor1 * valor2
    elif operacion == '/':
        return valor1 / valor2

@register.filter
def getDataPieChart(listTagData:List[TagData]):
    listTagDataCopy = copy.deepcopy(listTagData)
    listTagDataCopy.pop()
    itemTotal = listTagData[-1]
    data = ""
    for item in listTagDataCopy:
        porcentajeDouble = round((item.total * 100) / itemTotal.total, 2)
        porcentaje = str(porcentajeDouble).replace(',', '.')
        data += "{{ name:'{}\', y:{} }}, ".format(item.tagName, porcentaje)
    return data

@register.filter
def getDataBarChart(listTagData:List[TagData]):
    listTagDataCopy = copy.deepcopy(listTagData)
    listTagDataCopy.pop()
    return listTagDataCopy

@register.filter
def getHeightBarChart(listTagData:List[TagData]):
    return (len(listTagData)-1) * 45

@register.filter
def dinero(cantidad:int, mostarSigno=False):
    strCantidad = "$ {}".format(puntomil(cantidad))
    signo = ""
    if mostarSigno:
        if cantidad > 0: signo = '+ '
        elif cantidad < 0: signo = "- "
    return signo + strCantidad

@register.filter
def colorCantidad(cantidad):
    if cantidad == 0: 
        return ""
    elif cantidad > 0: 
        return "text-primary"
    elif cantidad < 0: 
        return "text-danger"

@register.filter
def checkedPagoMultiplePrestamo(valor1, valor2):
    if valor1 > 0 and valor2 == 0:
        return 'checked'

@register.filter
def valorPagoMultiplePrestamo(meDeben, yoDebo):
    if meDeben > 0 and yoDebo > 0:
        return 0
    elif meDeben > 0 and yoDebo == 0:
        return meDeben
    elif meDeben == 0 and yoDebo > 0:
        return yoDebo

@register.filter
def tipoPrestamoPublico(tipoPrestamo):
    if tipoPrestamo == "yopresto":
        return "Debo"
    elif tipoPrestamo == "meprestan":
        return "Me deben"
    else:
        return ""

@register.filter
def estadoSolicitudPrestamo(estado:int):
    nombreEstados = ["Creada", "Aprobada", "Rechazada"]
    return nombreEstados[estado]

@register.filter
def tipoPrestamo(tipoPrestamo:str, userpersona=None):
    if not userpersona:
        return "Yo presto" if tipoPrestamo == "yopresto" else "Me prestan"
    else:
        return "Me prestan" if tipoPrestamo == "yopresto" else "Yo presto"

@register.filter
def infoSolicitudPrestamo(solicitudPrestamo) -> str:
    nombreCuenta =  solicitudPrestamo.cuenta.nombre if solicitudPrestamo.cuenta else 'Ninguna'
    fechaStr = solicitudPrestamo.fechaPrestamo if hasattr(solicitudPrestamo, 'fechaPrestamo') else solicitudPrestamo.fechaPago
    # if not fechaStr: # si sigue vacio quiere decir que no se selecciono una fecha diferente, por lo cual se toma la fecha de la solicitud
    #     fechaStr = solicitudPrestamo.fechaSolicitud.strftime("%Y-%m-%d %H:%M:%S.%f") # se convierte a str para despues poderle darle manejo como str
    #     print("solicitudPrestamo.fechaSolicitud", solicitudPrestamo.fechaSolicitud)
    try:
        fechaDateTime = datetime.strptime(fechaStr, "%Y-%m-%d %H:%M:%S.%f")
    except:
        fechaDateTime = datetime.strptime(fechaStr, "%Y-%m-%d %H:%M:%S")
    fecha_formateada = fechaDateTime.strftime("%d/%m/%Y %I:%M %p")    
    return "Cuenta: {}. \nInfo: {}. \nFecha: {}".format(nombreCuenta, solicitudPrestamo.info, fecha_formateada)

@register.filter
def pagoMultiple(pagoMultiple:bool) -> str:
    return 'Multiple' if pagoMultiple else 'Individual'

@register.filter
def notificationColor(read:bool) -> str:
    return 'secondary' if read else 'primary'

@register.filter
def ReducirDecimales(valor, nDecimales):
    return format(valor, '.{}f'.format(nDecimales))

@register.filter
def DineroSinDecimales(valor):
    return dinero(int(valor))