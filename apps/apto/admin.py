from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import *

class ApartamentoResource(resources.ModelResource):
    class Meta:
        model = Apartamento

class ApartamentoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','nombre']
    list_display = ('id','nombre', )
    resource_class = ApartamentoResource

class PagadorResource(resources.ModelResource):
    class Meta:
        model = Pagador

class PagadorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','user__username']
    list_display = ('id','user',)
    resource_class = PagadorResource

class PersonaPagadorResource(resources.ModelResource):
    class Meta:
        model = PersonaPagador

class PersonaPagadorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','nombre','pagador__user__username']
    list_display = ('id','nombre','pagador',)
    resource_class = PersonaPagadorResource

class EstadiaResource(resources.ModelResource):
    class Meta:
        model = Estadia

class EstadiaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','fechaInicio','fechaFin']
    list_display = ('id','fechaInicio','fechaFin','persona',)
    resource_class = EstadiaResource

class EmpresaResource(resources.ModelResource):
    class Meta:
        model = Empresa

class EmpresaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','nombre']
    list_display = ('id','nombre', )
    resource_class = EmpresaResource

class PeriodoResource(resources.ModelResource):
    class Meta:
        model = Periodo

class PeriodoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','nombre']
    list_display = ('id','nombre',)
    resource_class = PeriodoResource

class ReciboResource(resources.ModelResource):
    class Meta:
        model = Recibo

class ReciboAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','periodo','valorPago','fechaInicio','fechaFin']
    list_display = ('id','periodo','valorPago','fechaInicio','fechaFin','empresa',)
    resource_class = ReciboResource

class PagadorReciboResource(resources.ModelResource):
    class Meta:
        model = PagadorRecibo

class PagadorReciboAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','valorPago','pagador','recibo']
    list_display = ('id','valorPago','pagador','recibo',)
    resource_class = PagadorReciboResource

class PeriodoPrestamoPersonaResource(resources.ModelResource):
    class Meta:
        model = PeriodoPrestamoPersona

class PeriodoPrestamoPersonaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','periodo','prestamo','persona']
    list_display = ('id','periodo','prestamo','persona',)
    resource_class = PeriodoPrestamoPersonaResource

admin.site.register(Pagador, PagadorAdmin)
admin.site.register(Apartamento, ApartamentoAdmin)
admin.site.register(PersonaPagador, PersonaPagadorAdmin)
admin.site.register(Estadia, EstadiaAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Periodo, PeriodoAdmin)
admin.site.register(Recibo, ReciboAdmin)
admin.site.register(PagadorRecibo, PagadorReciboAdmin)
admin.site.register(PeriodoPrestamoPersona, PeriodoPrestamoPersonaAdmin)