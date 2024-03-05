from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import secrets
import string
from .models import *
from apps.contabilidad.models import *

@login_required
def generarToken(request):
    caracteres = string.ascii_letters + string.digits
    token = Token(
        token = ''.join(secrets.choice(caracteres) for _ in range(10)),
        data = "|",
    )
    token.save()
    return redirect("/admin/publico/token/{}/change/".format(token.id))

def resumenPrestamos(request, token):
    tokenData = getTokenData(token)
    if tokenData:
        if "PersonaId" in tokenData:
            persona = get_object_or_404(Persona, id=int(tokenData["PersonaId"]))
            prestamos = Prestamo.objects.filter(persona=persona, cancelada=False)
            yoDebo = 0
            meDeben = 0
            for p in prestamos:
                if p.tipo == 'meprestan': 
                    yoDebo += p.saldo_pendiente
                elif p.tipo == 'yopresto':
                    meDeben += p.saldo_pendiente
            
            context = {
                "token": token,
                "persona": persona, 
                "yoDebo": yoDebo,
                "meDeben": meDeben
            }
            return render(request, 'publico/resumenPrestamos.html', context)
    raise Http404("No se encontró la página")
    
def vistaPrestamo(request, prestamoId, token):
    tokenData = getTokenData(token)
    if tokenData:
        if "PersonaId" in tokenData:
            persona = get_object_or_404(Persona, id=int(tokenData["PersonaId"]))
            prestamo =  get_object_or_404(Prestamo, id=prestamoId, persona=persona)
            context = {
                "prestamo": prestamo,
                "token": token,
                "transaccionesPago":TransaccionPrestamo.objects.filter(prestamo=prestamo, tipo=2).all()
            }
            return render(request, 'publico/vistaPrestamo.html', context)
    raise Http404("No se encontró la página")

def getTokenData(token):
    token = Token.objects.filter(token=token, active=True).first()
    if token:
        dataArray = token.data.split("|")
        if len(dataArray)%2 == 0:
            data = {}
            cont = 0
            while cont < len(dataArray):
                data[dataArray[cont]] = dataArray[cont+1]
                cont = cont + 2  
            return data
    return None
        
