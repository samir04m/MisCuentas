from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from datetime import datetime
from copy import deepcopy
from enum import Enum
from .forms import RegistroUsuarioForm
from .models import *
from .userSettingFuncs import *

class RegistroUsuario(CreateView):
    model = User
    template_name = 'registration/registro.html'
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('user:confirm_registro')

class NotificationType(Enum):
    General = 0
    PagoPrestamo = 1

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

@login_required
def userNotificationView(request, type:int, personaId:int):
    titles = ['Notificaciones', 'Pagos de prestamos']
    notifications = UserNotification.objects.filter(user=request.user).all()
    if type != 0:
        notifications = notifications.filter(type=type).all()
    if personaId != 0:
        notifications = notifications.filter(persona__id=personaId).all()

    notificationsCopy = [(deepcopy(n)) for n in notifications]
    for n in notifications:
        if not n.read:
            n.read = True
            n.save()

    paginator = Paginator(notificationsCopy, 10)
    page = request.GET.get('page')
    paginatedNotifications = paginator.get_page(page)

    context = {
        "title": titles[type],
        "notifications": paginatedNotifications
    }
    return render(request, 'user/userNotificationView.html', context)

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

def createUserNotification(message:str, user:User, type:NotificationType, persona:Persona=None):
    userNotification = UserNotification(
        message = message,
        user = user,
        persona = persona,
        date = datetime.now(),
        type=type.value
    )
    userNotification.save()
