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
