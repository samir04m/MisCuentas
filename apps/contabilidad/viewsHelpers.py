from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *

@login_required
def relacionarUsuarioConTransaccion(request):
    transacciones = Transaccion.objects.filter(user=None)
    cont = 0
    for transaccion in transacciones:
        if transaccion.cuenta:
            transaccion.user = transaccion.cuenta.user
            transaccion.save()
            cont += 1

    if transacciones.count() > 0:
        text = "Se han relacionado {} transacciones".format(str(transacciones.count()))
        alert(request, text)
    else:
        alert(request, 'Todas las transacciones estan relacionadas', 'i')

    return redirect('panel:inicio')