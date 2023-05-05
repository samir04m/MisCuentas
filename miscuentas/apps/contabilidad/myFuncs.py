from datetime import datetime
from .models import *

def crearTransaccion(tipo, cuenta:Cuenta, cantidad, info, tag, user:User, fecha=datetime.now()):
    saldo_anterior = 0
    if cuenta:
        saldo_anterior = cuenta.saldo
        if tipo == 'egreso':
            if cuenta.saldo < cantidad:
                raise Exception("No es posible realizar la transacción porque la cuenta no tiene el saldo suficiente")
            else:
                cuenta.saldo = cuenta.saldo - cantidad
        elif tipo == 'ingreso':
            cuenta.saldo = cuenta.saldo + cantidad
        cuenta.save()

    transaccion = Transaccion(
        tipo=tipo,
        saldo_anterior=saldo_anterior,
        cantidad=cantidad,
        info=info,
        fecha=fecha,
        cuenta=cuenta,
        etiqueta=getEtiqueta(tag, user),
        user=user
    )
    transaccion.save()
    return transaccion

def crearPrestamo(tipo, cantidad, info, cuenta:Cuenta, persona:Persona):
    fecha = datetime.now()
    if tipo == 'yopresto':
        crearTransaccion('egreso', cuenta, cantidad, info, 'Prestamo', persona.user, fecha)
    if tipo == 'meprestan':
        crearTransaccion('ingreso', cuenta, cantidad, info, 'Prestamo', persona.user, fecha)
    prestamo = Prestamo(
        tipo=tipo,
        cantidad=cantidad,
        info=info,
        saldo_pendiente=cantidad,
        fecha=fecha,
        cuenta=cuenta,
        persona=persona
    )
    prestamo.save()
    return prestamo

def getEtiqueta(nombre, user):
    etiqueta = Etiqueta.objects.filter(nombre=nombre, user=user).first()
    if not etiqueta:
        etiqueta = Etiqueta(nombre=nombre, tipo=getTipoEtiqueta(nombre), user=user)
        etiqueta.save()
    return etiqueta

def getTipoEtiqueta(nombre) -> int:
    tipo2 = ['Prestamo', 'Transferencia']
    if nombre in tipo2:
        return 2
    else:
        return 1

def eliminarTransaccion(transaccion):
    cuenta = transaccion.cuenta
    if cuenta:
        if transaccion.tipo == 'ingreso':
            cuenta.saldo -= transaccion.cantidad
        else:
            cuenta.saldo += transaccion.cantidad
        cuenta.save()
    transaccion.delete()

def getDate(inputDate):
    now = datetime.now()
    if inputDate:
        grupos = inputDate.split(" ")
        fecha = grupos[0].split("/")
        hora = grupos[1].split(":")
        hour = getHour24(hora[0], grupos[2])
        date = datetime(int(fecha[2]), int(fecha[1]), int(fecha[0]), hour, int(hora[1]), now.second)
        return date
    else:
        return now

def getHour24(hour, xm):
    if xm == "AM" and hour == "12":
        return 0
    elif xm == "AM":
        return int(hour)
    elif xm == "PM" and hour == "12":
        return int(hour)
    else:
        return int(hour) + 12

def validarMiles(cantidad) -> int:
    if len(str(cantidad)) < 4:
        return cantidad * 1000
    else:
        return cantidad