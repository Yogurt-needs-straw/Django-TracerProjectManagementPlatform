
from django import forms
from django.core.exceptions import ValidationError

from web import models
from web.forms.BootStrapForm import BootStrapForm

class ProjectModelForm(BootStrapForm, forms.ModelForm):
    # 修改model.form属性方式一
    # desc = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.Project
        fields = ['name', 'color', 'desc']
        # 重写插件属性
        widgets = {
            'desc': forms.Textarea
        }

    # 重写init方法，添加request参数
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        ''' 项目校验 '''
        name = self.cleaned_data['name']
        # 1.当前用户是否已创建过此项目
        exists = models.Project.objects.filter(name=name, creator=self.request.tracer.user).exists()
        if exists:
            raise ValidationError('项目名已存在')

        # 2.当前用户是否还有额度创建项目
        # 最多创建N个项目
        self.request.tracer.price_policy.project_num

        # 现在已创建多少项目
        count = models.Project.objects.filter(creator=self.request.tracer.user).count()

        # 项目允许数判断
        if count >= self.request.tracer.price_policy.project_num:
            raise ValidationError('项目个数超限，请购买套餐')

        return name


