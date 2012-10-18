from django.contrib import admin
from Spout.models import *


class AppAdmin(admin.ModelAdmin):

    list_display = ('product', 'name', 'version', 'note', 'creation_date', 'uuid')
    list_filter = ('product', 'name', 'tags',)

admin.site.register(App, AppAdmin)

class ProductAdmin(admin.ModelAdmin):

    list_display = ('name',)

admin.site.register(Product, ProductAdmin)

class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'description',)

admin.site.register(Tag, TagAdmin)    
