from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Count, Sum
from datetime import datetime
from apps.usuario.models import UserSetting
from apps.usuario.userSettingFuncs import *
from apps.contabilidad.models import *
from apps.contabilidad.myFuncs import getSaldoTotalCuentas, getDeudaTarjetasCredito, getDeudaPrestamos
from .myFuncs import *
from apps.contabilidad.myFuncs import getEtiquetaById

@login_required
def general(request):
    saldoTotalCuentas = getSaldoTotalCuentas(request)
    infoDeudaTC = getDeudaTarjetasCredito(request)
    deudaPrestamos = getDeudaPrestamos(request)
    saldoFinal = saldoTotalCuentas + deudaPrestamos.meDeben - infoDeudaTC.deudaPropia - deudaPrestamos.yoDebo
    if infoDeudaTC.deudaPropia > 0: infoDeudaTC.deudaPropia *= -1
    if deudaPrestamos.yoDebo > 0: deudaPrestamos.yoDebo *= -1

    context = {
        "saldoTotalCuentas": saldoTotalCuentas,
        "deudaTarjetasCredito": infoDeudaTC.deudaPropia,
        "deudaPrestamos": deudaPrestamos,
        "saldoFinal": saldoFinal
    }
    return render(request, 'reporte/general.html', context)

@login_required
def egresos_diarios(request):
    egresos = (
        Transaccion.objects.filter(user=request.user, tipo='egreso', estado__in=getEstadoTransaccion(request.user))
        .exclude(etiqueta__tipo__in=[2,3])
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
    numeroDias = 40
    cont = numeroDias
    for egreso in egresosOrdenados:
        datosGrafica.insert(0, egreso)
        cont -= 1
        if cont == 0:
            break

    context = {
        "numeroDias": numeroDias,
        "egresos": egresosOrdenados, 
        "grafica": datosGrafica, 
        "alertData":getAlertIncluirTransaccionesProgramadas(request.user)
    }
    return render(request, 'reporte/diario_egreso.html', context)


@login_required
def ingresos_diarios(request):
    ingresos = (
        Transaccion.objects.filter(user=request.user, tipo='ingreso')
        .exclude(etiqueta__tipo__in=[2,3])
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
        Transaccion.objects.filter(user=request.user, tipo='egreso', estado__in=getEstadoTransaccion(request.user))
        .exclude(etiqueta__tipo__in=[2,3])
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
    numeroMeses = 12
    cont = numeroMeses
    for egreso in egresosOrdenados:
        datosGrafica.insert(0, egreso)
        cont -= 1
        if cont == 0:
            break

    context = {
        "numeroMeses": numeroMeses,
        "egresos": egresosOrdenados, 
        "grafica": datosGrafica, 
        "alertData":getAlertIncluirTransaccionesProgramadas(request.user)
    }
    return render(request, 'reporte/mensual_egreso.html', context)

@login_required
def ingresos_mensuales(request):
    ingresos = (
        Transaccion.objects.filter(user=request.user, tipo='ingreso')
        .exclude(etiqueta__tipo__in=[2,3])
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
def cambiar_periodo_reporte_etiqueta_mensual(request):
    month = 0
    year = 0
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
    return redirect('reporte:reporte_etiqueta_mensual', month, year)

@login_required
def cambiar_periodo_reporte_subtag_mensual(request):
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    etiquetaId = 0
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        etiquetaId = int(request.POST.get('etiqueta'))
    return redirect('reporte:reporte_subtag_mensual', etiquetaId, year+'-'+month)

@login_required
def reporte_etiqueta_mensual(request, month, year):
    mes = datetime.today().month if month < 1 or month > 12 else month
    anio = datetime.today().year if year < 1998 or year > 2098 else year

    egresosPorEtiqueta = createListTagData(
        Transaccion.objects.filter(user=request.user, tipo='egreso', estado__in=getEstadoTransaccion(request.user), fecha__month=mes, fecha__year=anio).exclude(etiqueta__tipo__in=[2,3])
    )
    ingresosPorEtiqueta = createListTagData(
        Transaccion.objects.filter(user=request.user, tipo='ingreso', estado__in=getEstadoTransaccion(request.user), fecha__month=mes, fecha__year=anio).exclude(etiqueta__tipo__in=[2,3])
    )
    if egresosPorEtiqueta and ingresosPorEtiqueta:
        totalEgresos = egresosPorEtiqueta[-1]
        totalIngresos = ingresosPorEtiqueta[-1]
        resumen = getResumenAhorroMes(totalIngresos.total, totalEgresos.total, mes, anio, request)
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
        'alertData':getAlertIncluirTransaccionesProgramadas(request.user)
    }
    return render(request, 'reporte/mensual_etiqueta.html', context)

@login_required
def reporte_subtag_mensual(request, etiquetaId, periodo):
    periodoSplited = periodo.split("-")
    year = int(periodoSplited[0])
    month = int(periodoSplited[1])
    mes = datetime.today().month if month < 1 or month > 12 else month
    anio = datetime.today().year if year < 1998 or year > 2098 else year
    
    egresosPorEtiqueta = createListSubTagData(
        Transaccion.objects.filter(user=request.user, tipo='egreso', estado__in=getEstadoTransaccion(request.user), fecha__month=mes, fecha__year=anio, etiqueta__id=etiquetaId, subtag__isnull=False).exclude(etiqueta__tipo__in=[2,3])
    )

    context = {
        'egresosPorEtiqueta' : egresosPorEtiqueta,
        # 'ingresosPorEtiqueta' : ingresosPorEtiqueta,
        'nombreMes' : nombreMeses[mes-1],
        'month' : convertMonthToString(mes),
        'year' : anio,
        'periodo' : convertMonthToString(mes)+'-'+str(anio),
        'selectMonth' : createSelectOption('month', mes),
        'selectYear' : createSelectOption('year', anio),
        'etiqueta': getEtiquetaById(etiquetaId),
        # 'resumen': resumen,
        # 'alertData':getAlertIncluirTransaccionesProgramadas(request.user)
    }
    return render(request, 'reporte/mensual_subtag.html', context)