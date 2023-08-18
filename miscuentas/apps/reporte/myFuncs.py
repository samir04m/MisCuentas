from apps.contabilidad.models import *
from apps.contabilidad.myFuncs import getFormatoDinero
from apps.usuario.models import UserSetting
from apps.usuario.views import getUserSetting, setUserSetting, getMetaAhorroMes
from typing import List

nombreMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

class TableData:
    def __init__(self, fecha, nregistros, total):
        self.fecha = fecha
        self.nregistros = nregistros
        self.total = total

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

class SelectOption:
    def __init__(self, value, text, selected = ''):
        self.value = value
        self.text = text
        self.selected = selected

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

def createListSubTagData(transacciones):
    listTagData = []
    total = TagData('Total periodo', -1)
    for transaccion in transacciones:
        total.sumar(transaccion.cantidad)
        td = getTagData(listTagData, transaccion.subtag.nombre)
        if td:
            td.sumar(transaccion.cantidad)
        else:
            newTd = TagData(transaccion.subtag.nombre, transaccion.subtag.id)
            newTd.sumar(transaccion.cantidad)
            listTagData.append(newTd)
    if listTagData:
        listTagData = sorted(listTagData, key=lambda x: x.tagName)
        listTagData.append(total)
    return listTagData

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

def getResumenAhorroMes(totalIngresos, totalEgresos, month, year, request):
    ahorro = totalIngresos - totalEgresos
    porcentaje = (totalEgresos * 100) / totalIngresos
    mensajeMetaAhorro = None
    if totalIngresos > totalEgresos:
        mensajeAhorro = 'Este mes se ahorró ' + getFormatoDinero(ahorro)
        metaAhorro = getMetaAhorroMes(month, year, request)
        if ahorro == metaAhorro:
            mensajeMetaAhorro = 'Cumpló con la meta de ahorro de {}'.format(getFormatoDinero(metaAhorro))
        elif ahorro > metaAhorro:
            mensajeMetaAhorro = 'Cumpló con la meta de ahorro de {} y además ahorró un extra de {}'.format(getFormatoDinero(metaAhorro), getFormatoDinero(ahorro-metaAhorro))
        else:
            mensajeMetaAhorro = 'No cumpló con la meta de ahorro de {}. Le hicieron falta {} para cumplirla.'.format(getFormatoDinero(metaAhorro), getFormatoDinero(metaAhorro-ahorro))
    else:
        ahorro = ahorro * -1
        mensajeAhorro = 'No se ahorró y se gastó mas de lo que ganó '

    return {
        'ahorro': ahorro,
        'mensajePorcentaje': "Gastó el {}% de los ingresos".format(truncate(porcentaje, 2)),
        'mensajeAhorro': mensajeAhorro,
        'mensajeMetaAhorro':mensajeMetaAhorro
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