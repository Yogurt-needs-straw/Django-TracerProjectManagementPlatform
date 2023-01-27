from django import forms

from web import models
from web.forms.BootStrapForm import BootStrapForm


class WikiModelForm(BootStrapForm, forms.ModelForm):

    class Meta:
        model = models.Wiki
        exclude = ['project', 'depth', ]

    # 重写init方法，重置展示方法，将本项目相关的文档展示出来，而不是所有文章
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 找到想要的字段把他绑定显示的数据重置

        # 添加不选择父文章，创建父文章
        total_data_list = [('', '请选择'), ]

        # 数据库中获取，当前项目所有的wiki标题
        data_list = models.Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list

