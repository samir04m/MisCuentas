from datetime import datetime, timedelta
from .models import *
# from apps.contabilidad.myFuncs import getFormatoDinero

def GetAptoFromRequest(request) -> Apartamento:
    pagador = Pagador.objects.filter(user=request.user).first()
    if not pagador:
        raise Exception('No es posible obtener el Apartamento desde el request')
    return pagador.apto

def CalcularNumeroDias(fechaInicioStr:str, fechaFinStr:str) -> int:
    fechaInicio = datetime.strptime(fechaInicioStr, "%Y/%m/%d")
    fechaFin = datetime.strptime(fechaFinStr, "%Y/%m/%d")
    diferencia = fechaFin - fechaInicio + timedelta(days=1)
    return abs(diferencia.days)

# class EstadiaPersona:
#     def __init__(self, persona:Persona, dia:datetime, estuvo:bool):
#         self.persona = persona
#         self.date = date
#         self.estuvo = estuvo

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
            for persona in pagador.persona_set.all():        
                for estadia in Estadia.objects.filter(persona=persona):
                    fechaInicioDt = datetime.strptime(estadia.fechaInicio, '%Y/%m/%d')
                    fechaFinDt = datetime.strptime(estadia.fechaFin, '%Y/%m/%d')
                    if fechaInicioDt <= fechaActual <= fechaFinDt:
                        diaEstadiaPersona.listaPersonas.append(persona)
                        if not persona in personasConConsumo:
                            personasConConsumo.append(persona)
        datosEstadia.append(diaEstadiaPersona)
        fechaActual += timedelta(days=1)
    for i in datosEstadia:
        print(i.dia, i.listaPersonas)
    # print('personasConConsumo', personasConConsumo)


    return {
        'listaDiaEstadiaPersona':datosEstadia,
        'personasConConsumo':personasConConsumo
    }

def ObtenerDatosTablaEstadiaPersona(recibo:Recibo, datosEstadiasPersonas):
    # datosEstadiasPersonas = ObtenerDatosEstadiasPersonas(recibo)
    estadiaPersonas = {}
    for persona in datosEstadiasPersonas['personasConConsumo']:
        estadiaPersonas[persona.nombre] = []

    listaDias = []
    for diaEstadiaPersona in datosEstadiasPersonas['listaDiaEstadiaPersona']:
        listaDias.append(diaEstadiaPersona.dia.strftime('%d'))
        for persona in datosEstadiasPersonas['personasConConsumo']:
            estuvo = 1 if persona in diaEstadiaPersona.listaPersonas else 0
            estadiaPersonas[persona.nombre].append(estuvo)    
    # print(estadiaPersonas)

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
        fila = [diaEstadiaPersona.dia.strftime('%Y-%m-%d')]
        for pagadorRecibo in listaPagadorRecibo:
            nPersonas = 0
            valorPagoDia = 0
            for persona in diaEstadiaPersona.listaPersonas:
                if persona.pagador == pagadorRecibo.pagador:
                    nPersonas += 1
                    valorPagoDia += valorDia/len(diaEstadiaPersona.listaPersonas)

            fila.append("{} persona(s) - ${}".format(nPersonas, format(valorPagoDia, '.2f')))
            pagadorRecibo.valorPago += valorPagoDia
        tableData.append(fila)
            
    print('valorDia', valorDia)
    for i in tableData:
        print(i)

    suma = 0
    for pagadorRecibo in listaPagadorRecibo:
        print(pagadorRecibo)
        pagadorReciboExistente = PagadorRecibo.objects.filter(recibo=pagadorRecibo.recibo, pagador=pagadorRecibo.pagador).first()
        # if pagadorReciboExistente:
        #     pagadorReciboExistente.valorPago = pagadorRecibo.valorPago
        #     pagadorReciboExistente.save()
        # else:
        #     pagadorRecibo.save()
        suma += pagadorRecibo.valorPago
    print('suma',suma)
    return {
        'nombresPagadores': nombresPagadores,
        'tableData': tableData
    }