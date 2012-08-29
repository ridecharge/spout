from django.contrib import admin
from EasyEas.models import *


class AppAdmin(admin.ModelAdmin):

    list_display = ('product', 'name', 'version',)
    list_filter = ('product', 'name')

admin.site.register(App, AppAdmin)

