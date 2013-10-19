from django.contrib import admin
from AppDistribution.models import *
from AppDistribution.forms import UploadBuildForm
from AppDistribution.utils import zipapps


#Stuff for admining custom user object

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.http import HttpResponseRedirect, HttpResponse
from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from django.forms.models import inlineformset_factory

#endstuff

from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from django.contrib.admin.options import InlineModelAdmin
admin.site.unregister(Site)
admin.site.unregister(Group)

class SpoutSiteAdmin(admin.ModelAdmin):
    
    list_display = ('home_page', )

admin.site.register(SpoutSite, SpoutSiteAdmin)

class AppAssetForm(forms.ModelForm):
    model = App.assets
    primary = forms.BooleanField()
    uuid = forms.CharField()

class AppAssetInline(admin.TabularInline):

    model = AppAsset
    readonly_fields = ('uuid', 'asset_type',)

    
class AppAdmin(admin.ModelAdmin):

    list_display = ('product', 'name', 'version', 'note', 'creation_date', 'download_count')
    list_filter = ('product', 'name', 'tags',)
    actions = ['create_zip']
    inlines = [AppAssetInline,]

    def create_zip(self, request, queryset):

        zipfile = zipapps.zip_apps_and_assets(queryset)
        thefile = open(zipfile.fp.name, "r")
        
        return HttpResponse(thefile, mimetype="application/zip")

    create_zip.short_description = "Download apps and related assets as zip"

    def icon_image(obj):
        return u"<img src='%s'>" % obj.icon_url
    icon_image.allow_tags = True


    exclude = ('icon',)
    readonly_fields = (icon_image, 'version', 'name', 'creation_date', 'download_count')

admin.site.register(App, AppAdmin)

class ProductAdmin(admin.ModelAdmin):

    list_display = ('name',)
    fields = ('name', )

admin.site.register(Product, ProductAdmin)

class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'description',)

admin.site.register(Tag, TagAdmin)    

class PageRowInline(admin.TabularInline):

    """
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print db_field.name
        if db_field.name == "tag":
            print kwargs
#            kwargs["queryset"] = Tag.objects.filter(apps__product=
        return super(PageRowInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
    """
    class Media:
        css = {
                "all" : ("css/admin.css",)
       }
    formfield_overrides = {
                        BitField: {'widget': BitFieldCheckboxSelectMultiple},
                            }

   
   

    model = PageRow

class PageAdmin(admin.ModelAdmin):

    change_form_template = "admin/change_form_w.html"
    readonly_fields = ('slug',)
    
    inlines = [PageRowInline]

admin.site.register(Page, PageAdmin)


class UserCreationForm(forms.ModelForm):
    """ Form for creating new users, including a repeated password."""

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    class Meta:
        model = SpoutUser
        fields = ('email', 'expiration_date',)

    def clean_password2(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):

        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()
    
    
    class Meta:
        model = SpoutUser

#    def clean_password(self):
#        return self.initial["password"]

class SpoutUserAdmin(UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'expiration_date', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
            (None, {'fields' : ('first_name', 'last_name', 'email', 'main_page', 'allowed_pages')}),
            ('Permissions info', {'fields' : ('is_admin',)}),
            ('Important dates', {'fields' : ('last_login', 'expiration_date',)}),
        )
    add_fieldsets = (
            (None, {
                'classes' : ('wide',),
                'fields' : ('username', 'first_name',
                    'last_name', 'email',
                    'expiration_date', 'password1', 
                    'password2', 'main_page',
                    'allowed_pages')}
            ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(SpoutUser, SpoutUserAdmin)

"""
class GroupAdmin(admin.ModelAdmin):
    model = Group
    list_display = ('name', 'main_page',)

admin.site.register(Group, GroupAdmin)

"""
