from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroUsuarioForm
from .models import *
from .userSettingFuncs import *

class RegistroUsuario(CreateView):
    model = User
    template_name = 'registration/registro.html'
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('user:confirm_registro')

@login_required
def switchUserSetting(request, key:str):
    value = getUserSetting(key, request.user)
    if value != None:
        newValue = 1 if value == 0 else 0
        setUserSetting(key, newValue, request.user)
    else:
        setUserSetting(key, 0, request.user)
    url_anterior = request.META.get('HTTP_REFERER')
    return redirect(url_anterior)

def confirm_registro(request):
    return render(request, 'registration/confirm_registro.html')

def getMetaAhorroMes(month:str, year:str, request) -> int:
    metaAhorro = getUserSetting("MetaAhorroMes_{}_{}".format(month, year), request.user)
    if not metaAhorro:
        metaAhorroMensual = getUserSetting('MetaAhorroMensual', request.user)
        if not metaAhorroMensual:
            metaAhorroMensual = 1500000
            setUserSetting('MetaAhorroMensual', metaAhorroMensual, request.user)
        metaAhorro = metaAhorroMensual
        setUserSetting("MetaAhorroMes_{}_{}".format(month, year), metaAhorroMensual, request.user)
    return metaAhorro