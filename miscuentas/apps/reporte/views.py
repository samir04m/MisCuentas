from django.shortcuts import render, redirect
from apps.contabilidad.models import *
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Count, Sum
from datetime import datetime
from apps.usuario.models import UserSetting
from apps.usuario.views import getUserSetting, setUserSetting

class TableData:
    def __init__(self, fecha, nregistros, total):
        self.fecha = fecha
        self.nregistros = nregistros
        self.total = total

@login_required
def egresos_diarios(request):
    egresos = (
        Transaccion.objects.filter(user=request.user, tipo='egreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(day=TruncDay('fecha'))
        .values('day')
        .annotate(numero=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    egresosOrdenados = []
    for dato in egresos:
        egresosOrdenados.insert(0, TableData(dato['day'], dato['numero'], dato['total']))
    egresosOrdenados.sort(key=lambda x: x.fecha, reverse=True)
    
    datosGrafica = []
    cont = 10
    for egreso in egresosOrdenados:
        datosGrafica.insert(0, egreso)
        cont -= 1
        if cont == 0:
            break

    context = {"egresos": egresosOrdenados, "grafica": datosGrafica}
    return render(request, 'reporte/diario_egreso.html', context)


@login_required
def ingresos_diarios(request):
    ingresos = (
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(day=TruncDay('fecha'))
        .values('day')
        .annotate(numero=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    ingresosOrdenados = []
    for dato in ingresos:
        ingresosOrdenados.insert(0, TableData(dato['day'], dato['numero'], dato['total']))
    ingresosOrdenados.sort(key=lambda x: x.fecha, reverse=True)
    
    datosGrafica = []
    cont = 10
    for egreso in ingresosOrdenados:
        datosGrafica.insert(0, egreso)
        cont -= 1
        if cont == 0:
            break

    context = {"ingresos": ingresosOrdenados, "grafica": datosGrafica}
    return render(request, 'reporte/diario_ingreso.html', context)


@login_required
def egresos_mensuales(request):    
    egresos = (
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='egreso')
        .exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(month=TruncMonth('fecha'))
        .values('month')
        .annotate(nRegistros=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    egresosOrdenados = []
    for dato in egresos:
        egresosOrdenados.insert(0, TableData(dato['month'], dato['nRegistros'], dato['total']))
    egresosOrdenados.sort(key=lambda x: x.fecha, reverse=True)

    datosGrafica = []
    cont = 10
    for egreso in egresosOrdenados:
        datosGrafica.insert(0, egreso)
        cont -= 1
        if cont == 0:
            break

    context = {"egresos": egresosOrdenados, "grafica": datosGrafica}
    return render(request, 'reporte/mensual_egreso.html', context)

@login_required
def ingresos_mensuales(request):
    ingresos = (
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(month=TruncMonth('fecha'))
        .values('month')
        .annotate(nRegistros=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    ingresosOrdenados = []
    for dato in ingresos:
        ingresosOrdenados.insert(0, TableData(dato['month'], dato['nRegistros'], dato['total']))
    ingresosOrdenados.sort(key=lambda x: x.fecha, reverse=True)

    datosGrafica = []
    cont = 10
    for ingreso in ingresosOrdenados:
        datosGrafica.insert(0, ingreso)
        cont -= 1
        if cont == 0:
            break

    context = {"ingresos": ingresosOrdenados, "grafica": datosGrafica}
    return render(request, 'reporte/mensual_ingreso.html', context)

@login_required
def consultar_periodo_etiquetas(request):
    month = 0
    year = 0
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
    return redirect('reporte:egresos_etiqueta', month, year)


nombreMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

class TagData:
    def __init__(self, tagName, tagId = 0):
        self.tagId = tagId
        self.tagName = tagName
        self.nRegistros = 0
        self.total = 0
    def __str__(self):
        return "{} - {} | {} | ${}".format(self.tagId, self.tagName, self.nRegistros, self.total)
    def sumar(self, cantidad):
        self.nRegistros += 1
        self.total += cantidad

def getTagData(lista, buscar):
    for i in lista:
        if i.tagName == buscar:
            return i
    return None

def convertMonthToString(intMes):
    if intMes < 10:
        return '0'+str(intMes)
    else:
        return str(intMes)

def createListTagData(transacciones):
    listTagData = []
    total = TagData('Total periodo', -1)
    for transaccion in transacciones:
        total.sumar(transaccion.cantidad)
        if not transaccion.etiqueta:
            td = getTagData(listTagData, 'Sin Etiqueta')
            if td:
                td.sumar(transaccion.cantidad)
            else:
                noTag = TagData('Sin Etiqueta', 0)
                noTag.sumar(transaccion.cantidad)
                listTagData.append(noTag)
        elif transaccion.etiqueta.tipo != 2:
            td = getTagData(listTagData, transaccion.etiqueta.nombre)
            if td:
                td.sumar(transaccion.cantidad)
            else:
                newTd = TagData(transaccion.etiqueta.nombre, transaccion.etiqueta.id)
                newTd.sumar(transaccion.cantidad)
                listTagData.append(newTd)
    if listTagData:
        listTagData = sorted(listTagData, key=lambda x: x.tagName)
        listTagData.append(total)
    return listTagData

class SelectOption:
    def __init__(self, value, text, selected = ''):
        self.value = value
        self.text = text
        self.selected = selected

def createSelectOption(selectName, selectedOption):
    selectOptions = []
    if selectName == 'month':
        cont = 0
        for mes in nombreMeses:
            cont += 1
            selected = 'selected' if cont == selectedOption else ''
            selectOptions.append(SelectOption(cont, mes, selected))
    elif selectName == 'year':
        year = selectedOption - 10
        iteraciones = 0
        while iteraciones < 20:
            iteraciones += 1
            selected = 'selected' if year == selectedOption else ''
            selectOptions.append(SelectOption(year, year, selected))
            year += 1
        
    return selectOptions

def getTransaccionesDelMes(tipo, user, mes, anio, incluirTP):
    if incluirTP:
        return Transaccion.objects.filter(user=user, tipo=tipo, fecha__month=mes, fecha__year=anio).exclude(etiqueta__tipo=2)
    else:
        return Transaccion.objects.filter(user=user, tipo=tipo, estado=1, fecha__month=mes, fecha__year=anio).exclude(etiqueta__tipo=2)

@login_required
def egresos_etiqueta(request, month, year):
    mes = datetime.today().month if month < 1 or month > 12 else month
    anio = datetime.today().year if year < 1998 or year > 2098 else year
    mensajeIncluirTP = getMensajeIncluirTransaccionesProgramadas(request.user)
    incluirTP = getUserSetting('IncluirTransaccionesProgramadas', request.user)

    egresosPorEtiqueta = createListTagData(getTransaccionesDelMes('egreso', request.user, mes, anio, incluirTP))
    ingresosPorEtiqueta = createListTagData(getTransaccionesDelMes('ingreso', request.user, mes, anio, incluirTP))

    if egresosPorEtiqueta and ingresosPorEtiqueta:
        totalEgresos = egresosPorEtiqueta[-1]
        totalIngresos = ingresosPorEtiqueta[-1]
        resumen = obtenerResumen(totalIngresos.total, totalEgresos.total)
    else:
        resumen = None

    context = {
        'egresosPorEtiqueta' : egresosPorEtiqueta,
        'ingresosPorEtiqueta' : ingresosPorEtiqueta,
        'nombreMes' : nombreMeses[mes-1],
        'month' : convertMonthToString(mes),
        'year' : anio,
        'periodo' : convertMonthToString(mes)+'-'+str(anio),
        'selectMonth' : createSelectOption('month', mes),
        'selectYear' : createSelectOption('year', anio),
        'resumen': resumen,
        'mensajeIncluirTP': mensajeIncluirTP
    }
    return render(request, 'reporte/mensual_etiqueta.html', context)


def obtenerResumen(totalIngresos, totalEgresos):
    diferencia = totalIngresos - totalEgresos
    porcentaje = (totalEgresos * 100) / totalIngresos
    if totalIngresos > totalEgresos:
        mensajeDiferencia = 'Este mes se ahorró '
    else:
        diferencia = diferencia * -1
        mensajeDiferencia = 'No se ahorró y se gastó de más '

    return {
        'diferencia': diferencia,
        'porcentaje': truncate(porcentaje, 2),
        'mensajeDiferencia': mensajeDiferencia
    }

def getMensajeIncluirTransaccionesProgramadas(user:User):
    value = getUserSetting('IncluirTransaccionesProgramadas', user)
    if value == None:
        value = 0
        setUserSetting('IncluirTransaccionesProgramadas', value, user)
    if value == 0:
        return 'Incluir transacciones programadas en el informe'
    elif value == 1:
        return 'No incluir transacciones programadas en el informe'


def truncate(number: float, max_decimals: int) -> float:
    int_part, dec_part = str(number).split(".")
    return float(".".join((int_part, dec_part[:max_decimals])))