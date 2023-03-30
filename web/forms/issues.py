
from django import forms

from web import models
from web.forms.BootStrapForm import BootStrapForm

class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        # 页面已有元素，排除页面已有元素
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
