from datetime import datetime, timedelta
from .models import *
from apps.contabilidad.myFuncs import getFormatoDinero, alert

def GetAptoFromRequest(request) -> Apartamento:
    pagador = Pagador.objects.filter(user=request.user).first()
    if not pagador:
        raise Exception('No es posible obtener el Apartamento desde el request')
    return pagador.apto

def GetPeriodo(nombrePeriodo:str) -> Periodo:
    periodo = Periodo.objects.filter(nombre=nombrePeriodo).first()
    if not periodo:
        periodo = Periodo(nombre=nombrePeriodo)
        periodo.save()
    return periodo

def GetApto(request) -> Apartamento:
    return request.user.pagador_set.first().apto

def GetPagadores(request):
    return Pagador.objects.filter(apto=GetApto(request)).all()

def GetEmpresaInternet() -> Empresa:
    return Empresa.objects.filter(nombre__icontains='Internet').first()

def GetFechasReciboInternet(periodo):
    fechaPeriodo = periodo.nombre.split('-')
    fechaInicioDT = datetime(int(fechaPeriodo[0]), int(fechaPeriodo[1]), 24)
    fechaFinDT = fechaInicioDT - timedelta(days=30)
    return {
        'fechaInicio': fechaInicioDT.strftime("%Y/%m/%d"),
        'fechaFin': fechaFinDT.strftime("%Y/%m/%d")
    }

def GetReciboInternetByPeriodo(request, periodo:Periodo, valorRecibo:int):
    empresa = GetEmpresaInternet()
    apto = GetApto(request)
    recibo = Recibo.objects.filter(periodo=periodo, empresa=empresa, apto=apto).first()
    if not recibo:
        fechasFacturacion = GetFechasReciboInternet(periodo)
        recibo = Recibo(
            periodo=periodo,
            valorPago=valorRecibo,
            apto=apto,
            empresa=empresa,
            diasFacturados=30,
            fechaInicio=fechasFacturacion['fechaInicio'],
            fechaFin=fechasFacturacion['fechaFin']
        )
        recibo.save()
    return recibo

def CalcularNumeroDias(fechaInicioStr:str, fechaFinStr:str) -> int:
    fechaInicio = datetime.strptime(fechaInicioStr, "%Y/%m/%d")
    fechaFin = datetime.strptime(fechaFinStr, "%Y/%m/%d")
    diferencia = fechaFin - fechaInicio + timedelta(days=1)
    return abs(diferencia.days)

class DiaEstadiaPersona:
    def __init__(self, dia:datetime):
        self.dia = dia
        self.listaPersonas = []

    def __str__(self):
        return "{} - {}".format(self.dia, len(self.listaPersonas))

def ObtenerDatosEstadiasPersonas(recibo:Recibo):
    datosEstadia = []
    personasConConsumo = []
    fechaActual = datetime.strptime(recibo.fechaInicio, "%Y/%m/%d")
    for dia in range(1, recibo.diasFacturados + 1):
        fechaActualStr = fechaActual.strftime('%Y/%m/%d')
        diaEstadiaPersona = DiaEstadiaPersona(fechaActual)
        for pagador in Pagador.objects.filter(apto=recibo.apto).all():
            for persona in pagador.personapagador_set.all():        
                for estadia in Estadia.objects.filter(persona=persona):
                    fechaInicioDt = datetime.strptime(estadia.fechaInicio, '%Y/%m/%d')
                    fechaFinDt = datetime.strptime(estadia.fechaFin, '%Y/%m/%d')
                    if fechaInicioDt <= fechaActual <= fechaFinDt:
                        diaEstadiaPersona.listaPersonas.append(persona)
                        if not persona in personasConConsumo:
                            personasConConsumo.append(persona)
        datosEstadia.append(diaEstadiaPersona)
        fechaActual += timedelta(days=1)

    return {
        'listaDiaEstadiaPersona':datosEstadia,
        'personasConConsumo':personasConConsumo
    }

def ObtenerDatosTablaEstadiaPersona(recibo:Recibo, datosEstadiasPersonas):
    estadiaPersonas = {}
    for persona in datosEstadiasPersonas['personasConConsumo']:
        estadiaPersonas[persona.nombre] = []

    listaDias = []
    for diaEstadiaPersona in datosEstadiasPersonas['listaDiaEstadiaPersona']:
        listaDias.append(diaEstadiaPersona.dia.strftime('%d'))
        for persona in datosEstadiasPersonas['personasConConsumo']:
            estuvo = 1 if persona in diaEstadiaPersona.listaPersonas else 0
            estadiaPersonas[persona.nombre].append(estuvo)    

    return {
        'listaDias': listaDias,
        'estadiaPersonas': estadiaPersonas
    }


class DiaPagador:
    def __init__(self, nPersonas, valorPagoDia):
        self.nPersonas = nPersonas
        self.valorPagoDia = valorPagoDia

def CalcularPagoRecibo(recibo:Recibo, datosEstadiasPersonas):
    valorDia = recibo.valorPago/recibo.diasFacturados
    listaPagadorRecibo = []
    nombresPagadores = []
    for pagador in Pagador.objects.filter(apto=recibo.apto).all():
        listaPagadorRecibo.append(PagadorRecibo(
            valorPago=0,
            pagador=pagador,
            recibo=recibo
        ))
        nombresPagadores.append(pagador.user.username)

    tableData = []
    for diaEstadiaPersona in datosEstadiasPersonas['listaDiaEstadiaPersona']:
        row = [diaEstadiaPersona.dia.strftime('%Y-%m-%d')]
        for pagadorRecibo in listaPagadorRecibo:
            diaPagador = DiaPagador(0,0)
            for persona in diaEstadiaPersona.listaPersonas:
                if persona.pagador == pagadorRecibo.pagador:
                    diaPagador.nPersonas += 1
                    diaPagador.valorPagoDia += valorDia/len(diaEstadiaPersona.listaPersonas)

            row.append(diaPagador)
            pagadorRecibo.valorPago += diaPagador.valorPagoDia
        tableData.append(row)

    sumaPagosPagadores = 0
    sumaPagosPagadores = round(sum([pagadorRecibo.valorPago for pagadorRecibo in listaPagadorRecibo]))
    if recibo.valorPago == sumaPagosPagadores:
        for pagadorRecibo in listaPagadorRecibo:
            pagadorReciboExistente = PagadorRecibo.objects.filter(recibo=pagadorRecibo.recibo, pagador=pagadorRecibo.pagador).first()
            valorPagoEntero = round(pagadorRecibo.valorPago)
            if pagadorReciboExistente:
                if pagadorReciboExistente.valorPago != valorPagoEntero:
                    pagadorReciboExistente.valorPago = valorPagoEntero
                    pagadorReciboExistente.save()
            else:
                pagadorRecibo.save()

    return {
        'listaPagadorRecibo': listaPagadorRecibo,
        'tableData': tableData,
        'sumaPagosPagadores': sumaPagosPagadores
    }

def GetTableDataRecibosPeriodo(periodo:Periodo, apto:Apartamento):
    pagadores = Pagador.objects.filter(apto=apto).all()
    # totalxPagador = {}
    tableData = []
    for recibo in Recibo.objects.filter(periodo=periodo, apto=apto).all():
        row = [recibo.empresa.nombre]
        suma = 0
        for pagador in pagadores:
            pagadorRecibo = PagadorRecibo.objects.filter(pagador=pagador, recibo=recibo).first()
            valorPago = pagadorRecibo.valorPago if pagadorRecibo else 0
            
            row.append(valorPago)
            suma += valorPago
        row.append(suma)
        row.append(recibo.valorPago)
        tableData.append(row)

    rowTotal = ['Total']
    for col in range(1, len(tableData[0])):
        sumaColumna = 0
        for fil in range(0, len(tableData)):
            sumaColumna += tableData[fil][col]
        rowTotal.append(sumaColumna)
    tableData.append(rowTotal)

    return {
        'pagadores': pagadores,
        'tableData': tableData
    }


