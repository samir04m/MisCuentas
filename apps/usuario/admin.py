from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User
from import_export import resources
from django.contrib import admin
from .models import *

class UserResource(resources.ModelResource):
    class Meta:
        model = User

class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['username','email','first_name','last_name']
    list_display = ('username','email','is_staff','is_superuser','is_active',)
    resource_class = UserResource

class UserSettingResource(resources.ModelResource):
    class Meta:
        model = UserSetting

class UserSettingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['key']
    list_display = ('key','value','user',)
    resource_class = UserSettingResource

admin.site.register(UserSetting, UserSettingAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)