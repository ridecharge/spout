from django import forms
from Spout import models

class UploadBuildForm(forms.Form):


    note = forms.CharField(max_length=255)
    app_package = forms.FileField()
    dsym_file = forms.FileField(required=False)
    file_type = forms.ChoiceField(models.APP_TYPE_CHOICES)
    product = forms.ModelChoiceField(models.Product.objects.all())


