
from django import forms
from django.core.exceptions import ValidationError

from web.forms.BootStrapForm import BootStrapForm
from web import models

class FolderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ['name']

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    # 判断是否已有相同的文件名
    def clean_name(self):
        name = self.cleaned_data['name']

        # 数据库判断 当前目录下 此文件是否已存在
        queryset = models.FileRepository.objects.filter(file_type=2, name=name, project=self.request.tracer.project)
        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists()
        else:
            exists = queryset.filter(parent__isnull=True).exists()

        # 如果存在表示 已有相同的文件名
        if exists:
            raise ValidationError('文件夹已存在')

        return name