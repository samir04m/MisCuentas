from django.shortcuts import render
from apps.contabilidad.models import *
from django.contrib.auth.decorators import login_required

from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Count, Sum

@login_required
def diario_egreso(request):
    egresos =  reversed( Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by() )

    chart_egresos = Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by()[:7]


    context = {"egresos":egresos, "chart_egresos":chart_egresos}
    return render(request, 'reporte/diario_egreso.html', context)

@login_required
def diario_ingreso(request):
    ingresos =  reversed( Transaccion.objects.filter(cuenta__user = request.user.id, tipo='ingreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by() )

    chart_ingresos = Transaccion.objects.filter(cuenta__user = request.user.id, tipo='ingreso') \
            .annotate(day=TruncDay('fecha')).values('day').annotate(nt=Count('id'), total=Sum('cantidad')).order_by()[:7]


    context = {"ingresos":ingresos, "chart_ingresos":chart_ingresos}
    return render(request, 'reporte/diario_ingreso.html', context)


@login_required
def mensual_egreso(request):
    egresos = Transaccion.objects.filter(cuenta__user = request.user.id, tipo='egreso'). \
        annotate(month=TruncMonth('fecha')).values('month').annotate(nt=Count('id'), total=Sum('cantidad')).order_by()
    print(egresos)
    for e in egresos:
        for i, n in e.items():
            print(type(i), i, n)
        print("--------------------")

    return render(request, 'reporte/mensual.html', {"egresos":egresos})
