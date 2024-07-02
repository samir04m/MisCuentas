from django.urls import path, include
from .views import *

urlpatterns = [
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('registro-exitoso/', confirm_registro, name='confirm_registro'),

    path('switchUserSetting/<str:key>/', switchUserSetting, name='switchUserSetting'),

    path('notifications/<int:type>/<int:personaId>/', userNotificationView, name='userNotificationView'),
]
