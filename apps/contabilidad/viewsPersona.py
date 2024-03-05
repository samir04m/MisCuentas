from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import request
from .models import *
from .forms import *
from .myFuncs import *
from apps.usuario.views import getUserSetting

@login_required
def crear_persona(request):
    if request.method == 'POST':
        persona = Persona(
            nombre = request.POST.get('nombre').capitalize(),
            user = request.user
        )
        persona.save()
        messages.success(request, 'Persona creada exitosamente', extra_tags='success')
        return redirect('panel:inicio')
    return render(request, 'contabilidad/persona/crear_persona.html')

@login_required
def vista_persona(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id, user=request.user.id)
    prestamos = Prestamo.objects.filter(persona=persona, cancelada=False)
    yoDebo = 0
    meDeben = 0
    for p in prestamos:
        if p.tipo == 'meprestan': 
            yoDebo += p.saldo_pendiente
        elif p.tipo == 'yopresto':
            meDeben += p.saldo_pendiente

    diferencia = meDeben-yoDebo if (yoDebo > 0 and meDeben > 0) else 0
    diferenciaMensaje = ""
    if diferencia > 0: 
        diferenciaMensaje = "Finalmente a usted le deben"
    elif diferencia < 0:
        diferenciaMensaje = "Finalmente usted debe"
    
    context = {
        "persona": persona, 
        "yoDebo": yoDebo,
        "meDeben": meDeben,
        "diferencia": abs(diferencia),
        "diferenciaMensaje": diferenciaMensaje,
        "cuentas": Cuenta.objects.filter(user=request.user),
        "mostrarSaldoCuentas":getUserSetting('MostrarSaldoCuentas', request.user)
    }
    return render(request, 'contabilidad/persona/vista_persona.html', context)

@login_required
def listar_personas(request):
    personas = Persona.objects.filter(user = request.user.id)
    return render(request, 'contabilidad/persona/listar_personas.html', {"personas":personas})

class EditarPersona(UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'contabilidad/persona/crear_persona.html'
    success_url = reverse_lazy('panel:listar_personas')

class EliminarPersona(DeleteView):
    model = Persona
    template_name = 'contabilidad/persona/persona_confirm_delete.html'
    success_url = reverse_lazy('panel:listar_personas')

@login_required
def ocultar_persona(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id, user=request.user.id)
    persona.visible = not persona.visible
    persona.save()
    return redirect(request.META.get('HTTP_REFERER')) # redirect url anterior vista anterior