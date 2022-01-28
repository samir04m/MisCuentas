from django.shortcuts import render
from apps.contabilidad.models import *
from django.contrib.auth.decorators import login_required

from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Count, Sum


@login_required
def egresos_diarios(request):
    # egresos =  reversed( Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso') \
    #     .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by()
    egresos = reversed(
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='egreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(day=TruncDay('fecha'))
        .values('day')
        .annotate(numero=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    chart_egresos = (
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='egreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(day=TruncDay('fecha'))
        .values('day')
        .annotate(nt=Count('id'), total=Sum('cantidad'))
        .order_by()[:7]
    )
    # for e in egresos:
    #     if e.etiqueta__nombre == 'Prestamo':
    #         egresos.pop()
    context = {"egresos": egresos, "chart_egresos": chart_egresos}
    return render(request, 'reporte/diario_egreso.html', context)


@login_required
def ingresos_diarios(request):
    # ingresos = reversed(Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso')
    #     .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by())
    ingresos = reversed(
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(day=TruncDay('fecha'))
        .values('day')
        .annotate(numero=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    chart_ingresos = (
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(day=TruncDay('fecha'))
        .values('day')
        .annotate(numero=Count('id'), total=Sum('cantidad'))
        .order_by()[:7]
    )

    context = {"ingresos": ingresos, "chart_ingresos": chart_ingresos}
    return render(request, 'reporte/diario_ingreso.html', context)


@login_required
def egresos_mensuales(request):
    # egresos = reversed(Transaccion.objects.filter(cuenta__user=request.user.id, tipo='egreso')
    # .annotate(month=TruncMonth('fecha')).values('month').annotate(nRegistros=Count('id'), total=Sum('cantidad')).order_by())
    egresos = reversed(
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='egreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(month=TruncMonth('fecha'))
        .values('month')
        .annotate(nRegistros=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    chart_egresos = (
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='egreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(month=TruncMonth('fecha'))
        .values('month')
        .annotate(nRegistros=Count('id'), total=Sum('cantidad'))
        .order_by()[:6]
    )
    context = {"egresos": egresos, "chart_egresos": chart_egresos}
    return render(request, 'reporte/mensual_egreso.html', context)

@login_required
def ingresos_mensuales(request):
    # ingresos = reversed(Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso')
    # .annotate(month=TruncMonth('fecha')).values('month').annotate(nRegistros=Count('id'), total=Sum('cantidad')).order_by())
    ingresos = reversed(
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(month=TruncMonth('fecha'))
        .values('month')
        .annotate(nRegistros=Count('id'), total=Sum('cantidad'))
        .order_by()
    )
    chart_ingresos = (
        Transaccion.objects.filter(cuenta__user=request.user.id, tipo='ingreso').exclude(etiqueta__nombre='Transferencia').exclude(etiqueta__nombre='Prestamo')
        .annotate(month=TruncMonth('fecha'))
        .values('month')
        .annotate(nRegistros=Count('id'), total=Sum('cantidad'))
        .order_by()[:6]
    )
    context = {"ingresos": ingresos, "chart_ingresos": chart_ingresos}
    return render(request, 'reporte/mensual_ingreso.html', context)


@login_required
def egresos_etiqueta(request):
    # egresosPorEtiquetas = Etiqueta.objects.filter(user = request.user.id).annotate(nRegistros=Count('id'),total=Sum('transaccion__cantidad'))
    etiquetas = Etiqueta.objects.filter(user=request.user.id)
    egresosPorEtiqueta = {}
    for e in etiquetas:
        if e.nombre != 'Transferencia' and e.nombre != 'Prestamo':
            transacciones = (
                Transaccion.objects.filter(etiqueta=e.id, tipo='egreso')
                .annotate(month=TruncMonth('fecha'))
                .values('month')
                .annotate(nRegistros=Count('id'), total=Sum('cantidad'))
                .order_by()
            )
            if transacciones:
                    egresosPorEtiqueta[e.nombre] = transacciones

    return render(request, 'reporte/etiqueta_egreso.html', {"egresosPorEtiqueta":egresosPorEtiqueta})
