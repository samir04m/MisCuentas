from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroUsuarioForm
from .models import *

class RegistroUsuario(CreateView):
    model = User
    template_name = 'registration/registro.html'
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('user:confirm_registro')

@login_required
def incluirTransaccionesProgramadas(request):
    value = getUserSetting('IncluirTransaccionesProgramadas', request.user)
    if value != None:
        newValue = 1 if value == 0 else 0
        setUserSetting('IncluirTransaccionesProgramadas', newValue, request.user)
    else:
        setUserSetting('IncluirTransaccionesProgramadas', 0, request.user)
    url_anterior = request.META.get('HTTP_REFERER')
    return redirect(url_anterior)

def confirm_registro(request):
    return render(request, 'registration/confirm_registro.html')

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
