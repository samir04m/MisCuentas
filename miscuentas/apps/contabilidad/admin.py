# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

admin.site.register(Cuenta)
admin.site.register(Etiqueta)
admin.site.register(Persona)
admin.site.register(Transaccion)
