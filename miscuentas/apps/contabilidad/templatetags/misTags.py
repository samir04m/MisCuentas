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
def fecha(fecha):
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    fecha_str = str(fecha.hour)+":"+str(fecha.minute)+" - "+str(fecha.day)+" "+meses[fecha.month-1]+" "+str(fecha.year)
    return fecha_str
