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
def sin_etiqueta(etiqueta):
    if not etiqueta: return "- - - - - -"
    else: return etiqueta

@register.filter
def invertir(querySet):
    return querySet.reverse()
