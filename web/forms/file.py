
from django import forms
from web.forms.BootStrapForm import BootStrapForm
from web import models

class FolderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ['name']

