from django.contrib import admin
from EasyEas.models import *


class AppAdmin(admin.ModelAdmin):

    list_display = ('product', 'name', 'version', 'approved', 'note',)
    list_filter = ('product', 'name', 'approved')

admin.site.register(App, AppAdmin)

class ProductAdmin(admin.ModelAdmin):

    list_display = ('name',)

admin.site.register(Product, ProductAdmin)

class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'description',)

admin.site.register(Tag, TagAdmin)    
