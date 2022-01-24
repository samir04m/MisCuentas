from django.shortcuts import render
from apps.contabilidad.models import *
from django.contrib.auth.decorators import login_required

from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Count, Sum

@login_required
def egresos_diarios(request):
    egresos =  reversed( Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by() )

    chart_egresos = Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by()[:7]

    context = {"egresos":egresos, "chart_egresos":chart_egresos}
    return render(request, 'reporte/diario_egreso.html', context)

@login_required
def ingresos_diarios(request):
    ingresos =  reversed( Transaccion.objects.filter(cuenta__user = request.user.id, tipo='ingreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by() )

    chart_ingresos = Transaccion.objects.filter(cuenta__user = request.user.id, tipo='ingreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by()[:7]


    context = {"ingresos":ingresos, "chart_ingresos":chart_ingresos}
    return render(request, 'reporte/diario_ingreso.html', context)


@login_required
def egresos_mensuales(request):
    egresos =  reversed( Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso') \
            .annotate(month=TruncMonth('fecha')).values('month').annotate(nRegistros=Count('id'), total=Sum('cantidad')).order_by() )

    chart_egresos = Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso') \
            .annotate(month=TruncMonth('fecha')).values('month').annotate(nRegistros=Count('id'), total=Sum('cantidad')).order_by()[:6]

    context = {"egresos":egresos, "chart_egresos":chart_egresos}
    return render(request, 'reporte/mensual_egreso.html', context)

@login_required
def ingresos_mensuales(request):
    ingresos =  reversed( Transaccion.objects.filter(cuenta__user = request.user.id, tipo='ingreso') \
            .annotate(month=TruncMonth('fecha')).values('month').annotate(nRegistros=Count('id'), total=Sum('cantidad')).order_by() )

    chart_ingresos = Transaccion.objects.filter(cuenta__user = request.user.id, tipo='ingreso') \
            .annotate(month=TruncMonth('fecha')).values('month').annotate(nRegistros=Count('id'), total=Sum('cantidad')).order_by()[:6]

    context = {"ingresos":ingresos, "chart_ingresos":chart_ingresos}
    return render(request, 'reporte/mensual_ingreso.html', context)


@login_required
def egresos_etiqueta(request):
    etiquetas = Etiqueta.objects.filter(user = request.user.id).annotate(nRegistros=Count('id'),total=Sum('transaccion__cantidad'))
    return render(request, 'reporte/etiqueta_egreso.html', {"etiquetas":etiquetas})
