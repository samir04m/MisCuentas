from django import template
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
def dinero(cantidad, mostarSigno=False):
    strCantidad = "${}".format(puntomil(cantidad))
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