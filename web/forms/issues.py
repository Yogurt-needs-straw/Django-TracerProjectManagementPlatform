
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

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 处理数据初始化

        # 获取当前项目的所有问题类型
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(
            project=request.tracer.project).values_list('id', 'title')

        # 获取当前项目的所有模块
