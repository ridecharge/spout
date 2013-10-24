from django import forms
from AppDistribution import models
from django.forms import ModelForm

class UploadBuildForm(forms.Form):


    note = forms.CharField(max_length=255)
    app_package = forms.FileField()
    dsym_file = forms.FileField(required=False)
    file_type = forms.ChoiceField(models.APP_TYPE_CHOICES)
    product = forms.CharField(max_length=255)

class UploadAppForm(forms.Form):

    product = forms.CharField(max_length=255)
    note = forms.CharField(max_length=255)
    tags = forms.CharField(max_length=255, required=False)
    device_type = forms.CharField(max_length=40)


    
class UploadAppAssetForm(ModelForm):
    class Meta:
        model = models.AppAsset
        exclude = ('app', 'uuid', 'asset_type',)


