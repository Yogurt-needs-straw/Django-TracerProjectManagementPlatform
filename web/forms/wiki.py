from django import forms

from web import models
from web.forms.BootStrapForm import BootStrapForm


class WikiModelForm(BootStrapForm, forms.ModelForm):

    class Meta:
        model = models.Wiki
        exclude = ['project']

