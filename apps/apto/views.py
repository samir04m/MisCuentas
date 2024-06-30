from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from apps.contabilidad.myFuncs import *
from .myFuncs import *
from .models import *

@login_required
def home(request):
    pagador = Pagador.objects.filter(user=request.user).first()
    context = {
        'recibos': Recibo.objects.filter(apto=pagador.apto).all(),
        'periodos': Periodo.objects.all() 
    }
    return render(request, 'apto/home.html', context)

@login_required
def recibosPeriodo(request, periodoId):
    periodo = get_object_or_404(Periodo, id=periodoId)
    pagador = Pagador.objects.filter(user=request.user).first()
    tableData = GetTableDataRecibosPeriodo(periodo, pagador.apto)
    context = {
        'periodo': periodo,
        'pagadores': tableData['pagadores'],
        'tableData': tableData['tableData']
    }
    return render(request, 'apto/recibosPeriodo.html', context)

@login_required
def crearRecibo(request):
    if request.method == 'POST':
        try:
            recibo = Recibo(
                valorPago = int(request.POST.get('valorPago').replace('.','')),
                fechaInicio = request.POST.get('fechaInicio'),
                fechaFin = request.POST.get('fechaFin'),
                diasFacturados = CalcularNumeroDias(request.POST.get('fechaInicio'), request.POST.get('fechaFin')),
                periodo = GetPeriodo(request.POST.get('periodo')),
                empresa = Empresa.objects.filter(id=int(request.POST.get('empresa'))).first(),
                apto = GetAptoFromRequest(request)
            )
            recibo.save()
            alert(request, 'Se registro el recibo correctamente')
        except Exception as ex:
            printException(ex)
            alert(request, 'No fue posible crear el recibo', 'e')
        return redirect('apto:home')

    context = {
        'empresas' : Empresa.objects.all()
    }
    return render(request, 'apto/crearRecibo.html', context)

@login_required
def vistaRecibo(request, id):
    recibo = get_object_or_404(Recibo, id=id)
    datosEstadiasPersonas = ObtenerDatosEstadiasPersonas(recibo)
    estadiaData = ObtenerDatosTablaEstadiaPersona(recibo, datosEstadiasPersonas)
    dataPago = CalcularPagoRecibo(recibo, datosEstadiasPersonas)
    context = {
        'recibo': recibo,
        'listaDias': estadiaData['listaDias'],
        'estadiaPersonas': estadiaData['estadiaPersonas'],
        'listaPagadorRecibo': dataPago['listaPagadorRecibo'],
        'tableData': dataPago['tableData'],
        'sumaPagosPagadores': dataPago['sumaPagosPagadores']
    }
    print('valores', type(recibo.valorPago), type(dataPago['sumaPagosPagadores']))
    print('valores', recibo.valorPago, dataPago['sumaPagosPagadores'])
    if recibo.valorPago != dataPago['sumaPagosPagadores']:
        print('diferente')
    else:
        print('igual')

    return render(request, 'apto/vistaRecibo.html', context)