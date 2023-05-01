from datetime import datetime
from apps.contabilidad.models import *

def crearTransaccion(tipo, cuenta:Cuenta, cantidad, info, tag, user:User, fecha=datetime.now()):
    transaccion = Transaccion(
        tipo=tipo,
        saldo_anterior=cuenta.saldo,
        cantidad=cantidad,
        info=info,
        fecha=fecha,
        cuenta=cuenta,
        etiqueta=getEtiqueta(tag, user),
        user=user
    )
    transaccion.save()
    if tipo == 'egreso':
        cuenta.saldo = cuenta.saldo - cantidad
    if tipo == 'ingreso':
        cuenta.saldo = cuenta.saldo + cantidad
    cuenta.save()
    return transaccion

def crearPrestamo(tipo, cantidad, info, cuenta:Cuenta, persona:Persona):
    fecha = datetime.now()
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
    if tipo == 'yopresto':
        crearTransaccion('egreso', cuenta, cantidad, info, 'Prestamo', persona.user, fecha)
    if tipo == 'meprestan':
        crearTransaccion('ingreso', cuenta, cantidad, info, 'Prestamo', persona.user, fecha)
    return prestamo

def getEtiqueta(nombre, user):
    etiqueta = Etiqueta.objects.filter(nombre=nombre, user=user).first()
    if not etiqueta:
        etiqueta = Etiqueta(nombre=nombre, user=user)
        etiqueta.save()
    return etiqueta