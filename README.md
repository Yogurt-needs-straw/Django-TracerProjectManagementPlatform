# Django-TracerProjectManagementPlatform

这个是一个项目管理平台

##### 1.完成用户管理

##### 2.星标

> 思路：在获取项目列表的同时，将用户创建项目以及参与项目，使用字典进行封装。
>
> value:表示项目信息
>
> type:表示项目类型

需注意使用path方法类型转化器

```python
path('test/<int:year>/', views.year_test),
Django 提供了自定义转换器。下面介绍 Django 默认支持的转换器，如下所示：
str，匹配除了路径分隔符（/）之外的非空字符串，这是默认的形式；
int，匹配正整数，包含0；
slug，匹配字母、数字以及横杠、下划线组成的字符串；
uuid，匹配格式化的 uuid，如 075194d3-6885-417e-a8a8-6c931e272f00；
path，匹配任何非空字符串，包含了路径分隔符。
```

2.1添加星标（项目收藏、特别关注）

```
我创建的项目：Project的star=True
我参与的项目：ProjectUser的star=True
```

2.2移除星标

```
我创建的项目：Project的star=False
我参与的项目：ProjectUser的star=False
```



##### 3.选择颜色

> 思路：1.排除默认添加的color插件，不添加form-control  2.不使用模板中的select radio标签。3.构建新的radio标签。4.隐藏radio选项，将色块显现，用css对色块形状进行修改。

3.1 **部分样式应用BootStrapForm**

```python
class BootStrapForm(object):

    bootstrap_class_exclude = []

    # 样式重写
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # 排除color选项 不添加 form-control
            if name in self.bootstrap_class_exclude:
                continue

            # 给所有标签添加class属性 form-control
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)

```

```python
class ProjectModelForm(BootStrapForm, forms.ModelForm):
    # 排除color插件 不添加 form-control  
    bootstrap_class_exclude = ['color']  # 排除默认添加

    class Meta:
		model = model.Project
        fields = "__all__"
```



3.2**定制ModelForm的插件**

```python
class ProjectModelForm(BootStrapForm, forms.ModelForm):
    
    class Meta:
        model = models.Project
        fields = "__all__"
        # 重写插件属性
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect(attrs={'class': 'color-radio'}),
        }
```

```python
from django.forms import RadioSelect


class ColorRadioSelect(RadioSelect):

    # template_name = 'django/forms/widgets/checkbox_select.html'
    # option_template_name = 'django/forms/widgets/checkbox_option.html'

    template_name = 'widgets/color_radio/radio.html'
    option_template_name = 'widgets/color_radio/radio_option.html'
```

template_name = 'widgets/color_radio/radio.html'

```django
{% with id=widget.attrs.id %}
    <div{% if id %} id="{{ id }}"{% endif %}{% if widget.attrs.class %} class="{{ widget.attrs.class }}"{% endif %}>
        {% for group, options, index in widget.optgroups %}
            {% for option in options %}
                <label {% if option.attrs.id %} for="{{ option.attrs.id }}"{% endif %} >
                    {% include option.template_name with widget=option %}
                </label>
            {% endfor %}
        {% endfor %}
    </div>
{% endwith %}

```

​    option_template_name = 'widgets/color_radio/radio_option.html'

```django
{% include "django/forms/widgets/input.html" %}
<span class="cycle" style="background-color:{{ option.label }}"></span>
```



3.3 **项目选择颜色**

3.1、3.2 知识点的应用 + 前端样式的编写



##### 4.切换菜单

> 思路：使用@register.inclusion_tag 装饰器 将切换菜单嵌入到 manage 模板文件中

```python
1.数据库中获取
	我创建的：
    我参与的：
2.循环显示
3.当前页面需要显示 / 其他页面也需要显示 [inclusion_tap]
```

```python
@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    ''' 菜单栏项目列表 '''
    # 1.获取创建的所有项目
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)

    # 2.获取参与的所有项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)

    return {"my": my_project_list, "join": join_project_list}
```



all_project_list.html

```html
<ul class="dropdown-menu">
    {# 判断是否有值 决定是否显示 #}

    {% if my %}
    {# 创建的项目   #}
    <li><i class="fa fa-list" aria-hidden="true"></i> 我创建的项目</li>
      {% for item in my %}
        <li><a href="#">{{ item.name }}</a></li>
      {% endfor %}
    <li role="separator" class="divider"></li>
    {% endif %}

    {% if join %}
    {# 参与的项目   #}
      <li><i class="fa fa-handshake-o" aria-hidden="true"></i> 我参与的项目</li>
      {% for item in join %}
        <li><a href="#">{{ item.project.name }}</a></li>
      {% endfor %}
    <li role="separator" class="divider"></li>
    {% endif %}

      <li><a href="/project/list">所有项目</a></li>
  </ul>
```

