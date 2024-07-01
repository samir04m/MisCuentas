from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.contabilidad.myFuncs import *
from apps.usuario.userSettingFuncs import getUserSetting
from apps.usuario.models import UserPersona
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
    context = {
        'recibo': recibo
    }
    if recibo.empresa != GetEmpresaInternet():
        context['reciboValorPagoFijo'] = False
        datosEstadiasPersonas = ObtenerDatosEstadiasPersonas(recibo)
        estadiaData = ObtenerDatosTablaEstadiaPersona(recibo, datosEstadiasPersonas)
        context['listaDias'] = estadiaData['listaDias']
        context['estadiaPersonas'] = estadiaData['estadiaPersonas']

        dataPago = CalcularPagoRecibo(recibo, datosEstadiasPersonas)
        context['listaPagadorRecibo'] = dataPago['listaPagadorRecibo']
        context['tableData'] = dataPago['tableData']
        context['sumaPagosPagadores'] = dataPago['sumaPagosPagadores']
    else:
        context['reciboValorPagoFijo'] = True
        pagadoresRecibos = PagadorRecibo.objects.filter(recibo=recibo).all()
        if not pagadoresRecibos:
            print('no existen calculo apgadores refirecionadno')
            return redirect('apto:addReciboInternet', recibo.periodo.id)
        context['listaPagadorRecibo'] = pagadoresRecibos

    return render(request, 'apto/vistaRecibo.html', context)

@login_required
def addReciboInternet(request, periodoId):
    periodo = get_object_or_404(Periodo, id=periodoId)
    valorRecibo = getUserSetting('ValorReciboInternet', request.user)
    if valorRecibo:
        seCreoPagadorReciboNuevo = False
        try:
            with transaction.atomic():
                pagadores = GetPagadores(request)
                recibo = GetReciboInternetByPeriodo(request, periodo, valorRecibo)
                for pagador in pagadores:
                    pagadorReciboExiste = PagadorRecibo.objects.filter(pagador=pagador, recibo=recibo).first()
                    if not pagadorReciboExiste:
                        pagadorRecibo = PagadorRecibo(
                            valorPago=round(valorRecibo/len(pagadores)),
                            pagador=pagador,
                            recibo=recibo
                        )
                        pagadorRecibo.save()
                        seCreoPagadorReciboNuevo = True
                if seCreoPagadorReciboNuevo:
                    alert(request, 'El recibo del internet se agregó correctamente')
                else:
                    alert(request, 'La información de pago del recibo de internet anteriormente', 'i')
        except Exception as ex:
            printException(ex)
            alert(request, 'Ocurrio un error al calcular la información de pago del recibo de internet', 'e')
        
    else:
        alert(request, 'No se ha establecido el valor del recibo', 'e')
    # return redirect('apto:recibosPeriodo', periodo.id)
    return RedireccionarVistaAnterior(request)

@login_required
def crearPrestamoRecibosPeriodo(request, periodoId, userId):
    periodo = get_object_or_404(Periodo, id=periodoId)
    user = get_object_or_404(User, id=userId)
    userPersona = UserPersona.objects.filter(admin=request.user, user=user).first()
    if userPersona:
        periodoPrestamoPersona = PeriodoPrestamoPersona.objects.filter(periodo=periodo, persona=userPersona.persona).first()
        if not periodoPrestamoPersona:
            try:
                with transaction.atomic():
                    infoPago = GetInfoPagosRecibosPeriodoUser(request, periodo, user)
                    prestamo = crearPrestamo(request, 'yopresto', infoPago['valorTotalPago'], infoPago['mensaje'], None, userPersona.persona)
                    periodoPrestamoPersona = PeriodoPrestamoPersona(
                        periodo=periodo,
                        prestamo=prestamo,
                        persona=userPersona.persona
                    )
                    periodoPrestamoPersona.save()
                    alert(request, 'Se ha creado el prestamo con '+user.username)
            except Exception as ex:
                printException(ex)
                alert(request, 'Ocurrio un error el intentar crear el prestamo', 'e')
        else:
            return redirect('panel:vista_prestamo', periodoPrestamoPersona.prestamo.id)
    else:
        alert(request, 'No se encontro una persona relacionada a este usuario', 'e')
    
    return RedireccionarVistaAnterior(request)