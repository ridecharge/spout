from django import forms
from EasyEas import models

class UploadBuildForm(forms.Form):


    note = forms.CharField(max_length=255)
    ipa_file = forms.FileField()
    dsym_file = forms.FileField()
    product = forms.ModelChoiceField(models.Product.objects.all())
