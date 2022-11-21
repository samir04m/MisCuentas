# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import *

from django.contrib.auth.models import User

class UserResource(resources.ModelResource):
    class Meta:
        model = User

class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['username','email','first_name','last_name']
    list_display = ('username','email','is_staff','is_superuser','is_active',)
    resource_class = UserResource

class CuentaResource(resources.ModelResource):
    class Meta:
        model = Cuenta

class CuentaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','nombre','user__username']
    list_display = ('id','nombre', 'saldo', 'user',)
    resource_class = CuentaResource

class EtiquetaResource(resources.ModelResource):
    class Meta:
        model = Etiqueta

class EtiquetaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','nombre','user__username']
    list_display = ('id','nombre', 'user',)
    resource_class = EtiquetaResource

class PersonaResource(resources.ModelResource):
    class Meta:
        model = Persona

class PersonaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','nombre','user__username']
    list_display = ('id','nombre', 'user',)
    resource_class = PersonaResource

class TransaccionResource(resources.ModelResource):
    class Meta:
        model = Transaccion

class TransaccionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','tipo','cuenta__nombre','etiqueta__nombre']
    list_display = ('id','cuenta','tipo','cantidad','etiqueta','fecha',)
    resource_class = TransaccionResource

class PrestamoResource(resources.ModelResource):
    class Meta:
        model = Prestamo

class PrestamoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','tipo','cuenta__nombre','persona__nombre']
    list_display = ('id','cuenta','tipo','cantidad','saldo_pendiente','persona','cancelada','fecha')
    resource_class = PrestamoResource

class TransaccionPrestamoResource(resources.ModelResource):
    class Meta:
        model = TransaccionPrestamo

class TransaccionPrestamoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id','transaccion','prestamo',)
    resource_class = TransaccionPrestamoResource

admin.site.register(Cuenta, CuentaAdmin)
admin.site.register(Etiqueta, EtiquetaAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(Transaccion, TransaccionAdmin)
admin.site.register(Prestamo, PrestamoAdmin)
admin.site.register(TransaccionPrestamo, TransaccionPrestamoAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
