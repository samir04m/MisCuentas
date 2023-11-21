from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib import admin
from .models import *

class TokenResource(resources.ModelResource):
    class Meta:
        model = Token

class TokenAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['id','token']
    list_display = ('id','token','data','active',)
    resource_class = TokenResource

admin.site.register(Token, TokenAdmin)