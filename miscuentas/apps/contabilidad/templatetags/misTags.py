from django import template
register = template.Library()

@register.filter
def puntomil(cantidad):
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
def textcolor(tipo):
    if tipo == 'ingreso': return 'text-primary'
    elif tipo == 'egreso': return 'text-danger'

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
