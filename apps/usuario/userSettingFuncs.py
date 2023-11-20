from django.contrib.auth.models import User
from .models import *

def getUserSetting(key, user:User):
    userSetting = UserSetting.objects.filter(user=user, key=key).first()
    if userSetting:
        value = userSetting.value
        if value.isdigit():
            return int(value)
        else:
            return value
    return None

def setUserSetting(key, value, user:User):
    userSetting = UserSetting.objects.filter(user=user, key=key).first()
    if userSetting:
        userSetting.value = value
    else:
        userSetting = UserSetting(
            key = key,
            value = value,
            user = user
        )
    userSetting.save()

def getAlertIncluirTransaccionesProgramadas(user:User):
    incluirTP = getUserSetting('IncluirTransaccionesProgramadas', user)
    if incluirTP:
        return AlertData('primary', 'Programadas incluidas!', 'En el reporte se estan incluyendo las transacciones programadas.', 'No incluir')
    else:
        if incluirTP == None:
            setUserSetting('IncluirTransaccionesProgramadas', 0, user)
        return AlertData('light', 'Solo realizadas!', 'En el reporte se estan incluyendo solo las transacciones realizadas.', 'Incluir programadas')

class AlertData:
    def __init__(self, color, titulo, mensaje, textoBoton):
        self.color = color
        self.titulo = titulo
        self.mensaje = mensaje
        self.textoBoton = textoBoton

def getEstadoTransaccion(user:User):
    incluirTP = getUserSetting('IncluirTransaccionesProgramadas', user)
    estados = [1, 2]
    if incluirTP:
        estados.append(0)
    return estados

def getUndefinedUserSettings(keys, user:User):
    sinDefinir = ""
    for key in keys:
        keyValue = getUserSetting(key, user)
        if keyValue == None or keyValue == "undefined":
            sinDefinir += key + ", "
            if keyValue == None:
                setUserSetting(key, "undefined", user)
    return sinDefinir
