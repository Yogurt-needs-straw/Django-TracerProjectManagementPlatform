
from django import forms

from web import models
from web.forms.BootStrapForm import BootStrapForm

class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        # 页面已有元素，排除页面已有元素
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']

        # 添加属性
        widgets = {
            "assign": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "attention": forms.SelectMultiple(attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
        }

