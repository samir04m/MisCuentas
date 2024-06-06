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
        'recibos' : Recibo.objects.filter()
    }
    return render(request, 'apto/home.html', context)

@login_required
def crearRecibo(request):
    if request.method == 'POST':
        try:
            recibo = Recibo(
                periodo = request.POST.get('periodo'),
                valorPago = int(request.POST.get('valorPago').replace('.','')),
                fechaInicio = request.POST.get('fechaInicio'),
                fechaFin = request.POST.get('fechaFin'),
                diasFacturados = CalcularNumeroDias(request.POST.get('fechaInicio'), request.POST.get('fechaFin')),
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