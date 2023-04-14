# Django-TracerProjectManagementPlatform

这是一个项目管理平台

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



##### 5.项目管理

> 思路：项目路由
>
> /manage/[项目id]/dashboard
>
> /manage/[项目id]/issues
>
> /manage/[项目id]/statistics
>
> /manage/[项目id]/file
>
> /manage/[项目id]/wiki
>
> /manage/[项目id]/setting

路由设计

```python
    # 进入项目管理
    # 使用路由分发
    path('manage/<int:project_id>/', include([
        path('dashboard/', manage.project_dashboard, name='project_dashboard'),
        path('issues/', manage.project_issues, name='project_issues'),
        path('statistics/', manage.project_statistics, name='project_statistics'),
        path('file/', manage.project_file, name='project_file'),
        path('wiki/', manage.project_wiki, name='project_wiki'),
        path('setting/', manage.project_setting, name='project_setting'),
    ], None)),
```

##### 5.1 进入项目展示菜单

```
- 进入项目
- 展示菜单
```

**5.1.1 是否已经进入项目？**【中间件】

判断URL是否是manage开头

project_id 判断 是否是该用户的 是什么类型的项目

**5.1.2 显示菜单**

依赖：是否已经进入项目？

```html
通过 request.tracer.project 判断
<ul class="nav navbar-nav">
      <li><a href="#">概述</a></li>
      <li><a href="#">wiki</a></li>
</ul>
```

**5.1.3 页面样式调整**

去掉 all_project_list 模板中的 `<ul class="nav navbar-nav">` ，在manage.html中添加`<ul>`标签，将项目菜单栏合为一个`<ul>`

**5.1.4 项目菜单默认选中**

> 思路：使用 inclusion_tag 实现项目切换

注意 django.urls 中的 reverse 用法 reverse("[app_name]:[urlname]")

```python
@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    data_list = [
        {'title': '概览', 'url': reverse("web:dashboard", kwargs={'project_id': request.tracer.project.id})},
        {'title': '问题', 'url': reverse('web:issues', kwargs={'project_id': request.tracer.project.id})},
        {'title': '统计', 'url': reverse('web:statistics', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'wiki', 'url': reverse('web:wiki', kwargs={'project_id': request.tracer.project.id})},
        {'title': '文件', 'url': reverse('web:file', kwargs={'project_id': request.tracer.project.id})},
        {'title': '配置', 'url': reverse('web:setting', kwargs={'project_id': request.tracer.project.id})},
    ]

    return {'data_list': data_list}
```

#### 6 wiki

- 表结构设计
- 快速开发
- 应用markdown组件
- 腾讯COS做上传

##### 6.1 表结构设计

| ID   | 标题 | 内容 | 项目ID | 父ID | 深度 |
| ---- | ---- | ---- | ------ | ---- | ---- |
| 1    | xx   | xxxx | 1      | null | 1    |
| 2    | xx   | xxxx | 2      | 1    | 2    |
| 3    |      |      | 3      | 1    | 2    |

**models.py**

```python
class Wiki(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='标题', max_length=32)
    content = models.TextField(verbose_name='内容')

    # 子关联  related_name 反向关联字段
    parent = models.ForeignKey(verbose_name='父文章', to='Wiki', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
```

**注意1：**

设置字段时，使用to时，在定义外键的时候加上"on_delete=“；

> 原因：django升级到2.0之后，表与表之间关联的时候必须写"on_delete"参数，否则会报错

例如：

```python
book = models.ForeignKey(BookInfo,on_delete=models.CASCADE)
```

扩展补充
(1)、on_delete = None：
删除关联表的数据时，当前表与关联表的filed的行为。
(2)、on_delete = models.CASCADE：
表示级联删除，当关联表（子表）中的数据删除时，与其相对应的外键（父表）中的数据也删除。
(3)、on_delete = models.DO_NOTHING:
你删你的，父亲（外键）不想管你
(4)、on_delete = models.PROTECT:
保护模式，如采用这个方法，在删除关联数据时会抛出ProtectError错误
(5)、on_delete = models.SET_DEFAULT:
设置默认值，删除子表字段时，外键字段设置为默认值，所以定义外键的时候注意加上一个默认值。
(6)、on_delete = models.SET（值）:
删除关联数据时，自定义一个值，该值只能是对应指定的实体
(7)、on_delete = models.SET_NULL
置空模式，删除时，外键字段被设置为空，前提就是blank=True, null=True,定义该字段时，允许为空。理解：删除关联数据（子表），与之关联的值设置默认值为null（父表中），这个前提需要父表中的字段可以为空。

**注意2：**

**通过主表来查询子表**

> A.objects.get(id=A_id).test.all().order_by('-created'),
>
> django 默认每个主表的对象都有一个是外键的属性，可以通过它来查询到所有属于主表的子表的信息。这个属性的名称默认是以子表的名称小写加上_set()来表示(上面默认以b_set访问)，默认返回的是一个querydict对象。
>
> related_name 可以给这个外键定义好一个别的名称

**通过子表来查询主表**

> B.objects.filter(a=A_id).order_by('-created')

**6.2 wiki开发**

6.2.1 wiki 首页展示

> 新建 wiki views展示页

**页面样式**

```html
<div class="container-fluid">
    <div class="panel panel-default">
      <div class="panel-heading"><i class="fa fa-book" aria-hidden="true"></i> wiki文档</div>
      <div class="panel-body">
          <div class="col-sm-3 title-list">
              目录
          </div>
          <div class="col-sm-9 content">
              <div style="text-align: center;margin-top: 50px;">
                  <h4> 《{{ request.tracer.project.name }}》wili文档库 </h4>
                  <a href="#">
                      <i class="fa fa-plus-circle" aria-hidden="true"></i> 新建文章
                  </a>
              </div>
          </div>
      </div>
    </div>
    </div>
```

**多级目录**

> 思路：
>
> 方式一：通过模板渲染。1.数据库获取数据带有层级的划分。2.将数据进行构造，通过字典类型返回。缺点：比较复杂、效率低
>
> - queryset = model.wiki.object.filter(project_id=2)
> - 数据构造 [{id:1,title:"",children:[]}]
>
> 方式二：后端+前端 结合实现，使用ajax与ID选择器
>
> - 前端：打开页面，发送ajax请求，获取所有的文章标题信息。
> - 后端：获取所有的文章信息。
>
> **知识点**：
>
> 1. .values 与 .values_list 返回数据类型不一样，.values返回的是字典数据类型，.values_list返回的是列表数据类型。
>
> 2. 调用JsonResponse会自动使用json.dumps进行数据类型格式化，但是Queryset类型无法被格式化会报错误，通过list转换成列表类型就可以了。

js加载显示

```javascript
function initCatalog() {
        $.ajax({
            url:"catalog/",
            type:"GET",
            dataType:"JSON",
            success:function (res) {
                if (res.status){
                    $.each(res.data, function (index, item) {
                        // item=[1, '123', null],
                        // 添加标签设置
                        var li = $("<li>").attr('id', "id_"+item.id).append($("<a>").text(item.title)).append($("<ul>"));
                        // 先处理父目录
                        if (!item.parent_id){
                            // 添加到catalog中
                            $("#catalog").append(li);
                        }else {
                            // 找到父标签然后添加
                            $("#id_"+item.parent_id).children('ul').append(li);
                        }
                    })
                }else {
                    alert("初始化目录失败");
                }
            }

        })
    }
```

多级目录展示部分存在两个问题：

- 父目录要提前出现：通过 排序 + 字段 (深度 depth) 将父级目录先展示出来

> 深度
>
> depth = models.IntegerField(verbose_name='深度', default=1)
>
> ```python
> # 判断用户是否已经选择了父文章
> if form.instance.parent:
>     form.instance.depth = form.instance.parent.depth + 1
> else:
>     form.instance.parent = 1
> ```

- 点击目录查看文章详细

> 通过判断 wiki/ 后是否带有 wiki_id
>
> ```python
> wiki_id = request.GET.get('wiki_id')
> if wiki_id:
>     print("文章详情页")
> else:
>     print("文章首页")
> ```
>
> 前端实现
>
> ```javascript
> // 文章连接url
> var href = WIKI_DETAIL_URL + "?wiki_id=" + item.id;
> // 添加标签设置
> var li = $("<li>").attr('id', "id_"+item.id).append($("<a>").text(item.title).attr('href', href)).append($("<ul>"));
> ```

6.2.2 添加文章

> 思路：1.使用Form表单提交添加的参数，使用reverse方法返回页面
>
> url = reverse('web:wiki', kwargs={'project_id': project_id})
>
> 2.重写init方法，重置展示方法，将本项目相关的文档展示出来，而不是所有文章
>
> 注意点：
>
> 1.使用在models中使用 `__str__` 对父文章进行关联显示标题信息
>
> ```python
> def __str__(self):
>  return self.title
> ```
>
> 2.通过创建自定义元组，将自定义元组返回给前端

```html
<div class="panel-body">
    <div class="col-sm-3 title-list">
        <div>目录</div>
    </div>
    <div class="col-sm-9 content">
        <form method="post">
            {% csrf_token %}
            {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {{ field }}
                <span class="error-msg">{{ field.errors.0 }}</span>
            </div>
            {% endfor %}
            <button type="submit" class="btn btn-primary">提 交</button>
        </form>
    </div>
</div>
```

forms/wiki

```python
class WikiModelForm(BootStrapForm, forms.ModelForm):

    class Meta:
        model = models.Wiki
        exclude = ['project']
```

views/wiki

```python
form = WikiModelForm(request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('web:wiki', kwargs={'project_id': project_id})
        # print(url)
        return redirect(url)
```

forms/wiki 重写init方法，重置展示方法，将本项目相关的文档展示出来，而不是所有文章。

```python
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 找到想要的字段把他绑定显示的数据重置

        # 添加不选择父文章，创建父文章
        total_data_list = [('', '请选择'), ]

        # 数据库中获取，当前项目所有的wiki标题
        data_list = models.Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list
```

6.2.3 预览文章

6.2.4 修改文章

6.2.5 删除文章

> 思路：获取到文章的 project_id 和 wiki_id 然后通过url进行删除

```python
path('wiki/delete/<int:wiki_id>/', wiki.delete, name='wiki_delete'),
```

**6.3应用Markdown编辑器**

> 思路：markdown编辑器，mdeditor
>
> 注意点：使用 z-index: 1001; 解决markdown全屏菜单栏显示问题
>
> ```css
> .editormd-fullscreen{
>     z-index: 1001;
> }
> ```

项目中想要应用markdown编辑器：

- 添加和编辑的页面中 textarea 输入框。-> 转换为markdown编辑器

  1. textarea框通过div包裹以便以后查找并转化为编辑器

     ```html
     <div id="editor">...</div>
     ```

  2. 应用 js 和 css

     ```html
     <link rel="stylesheet" href="{% static 'plugin/editor-md/css/editormd.min.css' %}">
     ```

     ```javascript
     <script src={% static 'plugin/editor-md/editormd.min.js' %}></script>
     ```

  3. 进行初始化
     ```js
     /*
         初始化markdown编辑器(textare转换为编辑器)
          */
     $(function () {
         initEdtorMd();
     });
     function initEdtorMd() {
         editormd("editor",{
             placeholder: "请输入内容",
             height: 500,
             path: "{% static 'plugin/editor-md/lib/' %}"
         })
     }
     ```


**使用markdown编辑器预览页面**

1. 内容区域

```html
<div id="previewMarkdown">
    <textarea>{{ wiki_object.content }}</textarea>
</div>
```

2. 引入css，js

```html
<link rel="stylesheet" href="{% static 'plugin/editor-md/css/editormd.preview.min.css' %}">
<script src={% static 'plugin/editor-md/editormd.min.js' %}></script>
<script src={% static 'plugin/editor-md/lib/marked.min.js' %}></script>
<script src={% static 'plugin/editor-md/lib/prettify.min.js' %}></script>
<script src={% static 'plugin/editor-md/lib/raphael.min.js' %}></script>
<script src={% static 'plugin/editor-md/lib/underscore.min.js' %}></script>
<script src={% static 'plugin/editor-md/lib/sequence-diagram.min.js' %}></script>
<script src={% static 'plugin/editor-md/lib/flowchart.min.js' %}></script>
<script src={% static 'plugin/editor-md/lib/jquery.flowchart.min.js' %}></script>
```

3. 初始化

```javascript
$(function () {
    previewMarkdown();
});
function previewMarkdown() {
    editormd.markdownToHTML("previewMarkdown", {
        htmlDebode:  "style,script,iframe"
    });
}
```

4. 通过markdown组件上传图片功能



**6.4 腾讯对象存储**

**6.4.1 开通腾讯对象存储以及创建桶**

**6.4.2 python实现上传文件**

- 使用 pip 安装（推荐）

  ```sh
   pip install -U cos-python-sdk-v5
  ```

**通过 COS 默认域名初始化（默认方式）**

通过 COS 默认域名访问时，SDK 会以 **{bucket-appid}.cos.{region}.myqcloud.com** 的域名形式访问 COS。

```python
# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = os.environ['COS_SECRET_ID']     # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = os.environ['COS_SECRET_KEY']   # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-beijing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)
```

> 注意：
>
> 正常情况下一个 region 只需要生成一个 CosS3Client 实例，然后循环上传或下载对象，不能每次访问都生成 CosS3Client 实例，否则 python 进程会占用过多的连接和线程。

> 说明：
>
> 关于临时密钥如何生成和使用，请参见 [临时密钥生成及使用指引](https://cloud.tencent.com/document/product/436/14048)。

```python
# 创建桶
response = client.create_bucket(
    Bucket='examplebucket-1250000000'
)
```

```python
# 上传文件
#### 高级上传接口（推荐）
# 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
response = client.upload_file(
    Bucket='examplebucket-1250000000',
    LocalFilePath='local.txt',  # 本地文件的路径
    Key='picture.jpg',   # 上传到桶之后的文件名
    PartSize=1,    
    MAXThread=10,
    EnableMD5=False
)
print(response['ETag'])
```

创建桶实例代码

```python
# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
# logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = 'xxxxx'
# 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140

secret_key = 'xxxxxx'
# 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140

region = 'ap-nanjing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
# token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
# scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

# 创建桶
response = client.create_bucket(
    Bucket='testbucket-1302900000',
    ACL='public-read',  # private / public-read / public-read-write
)
```

**6.5 项目中集成cos**

希望我们的项目中用到的图片可以放在cos中，防止我们的服务处理图片时压力过大。

**6.5.1 创建项目时创建桶**

```python
# 为项目创建一个桶
name = form.cleaned_data['name']
bucket = "{}-{}-bucket-{}-1302952368".format(name, request.tracer.user.mobile_phone, str(int(time.time())))
region = "ap-nanjing"
```



**6.5.2 markdown上传图片到cos**

> 思路：获取markdown上传对象标签 `editormd-image-file` ，随机生成对象名，使用文件上传函数，上传到该文件的对象桶中，将对象url返回后台，通过url展示到markdown页面上。
>
> 注意点：1.使用 @csrf_exempt 过滤 csrf token认证. 2.markdown编辑器中通过添加`imageUpload`、`imageFormats`、`imageUploadURL` 参数，使markdown编辑器增加本地上传文件功能。

- cos上传文件：本地文件；接收markdown上传的文件再进行上传到cos；
- markdown

**获取markdown上传对象标签 `editormd-image-file`** 

```python
image_object = request.FILES.get('editormd-image-file')
```

**随机生成对象名**

```python
# 随机函数
def uid(mobile_phone):
    ''' 不重复数据 '''
    data = "{}-{}".format(str(uuid.uuid4()), mobile_phone)
    # print(data)
    return md5(data)
```

```python
ext = image_object.name.rsplit('.')[-1]
random_filename = uid(request.tracer.user.mobile_phone)
key = "{}.{}".format(random_filename, ext)
```

**文件对象上传到当前项目的桶中**

```python
image_url = upload_file(
    request.tracer.project.bucket,
    request.tracer.project.region,
    image_object,
    key
)
```

#### 7.项目文件管理

功能介绍：

- 新建文件夹
- 上传文件

知识点：：

- 模态对话框 & ajax & modelForm校验
- 目录切换：展示当前文件夹 & 文件
- 删除文件夹：嵌套的子文件 & 子文件夹 全部删除
- 上传文件：js上传文件到cos
- 删除文件：删除数据库 以及 存储对象
- 进度条
- 下载文件

##### 7.1 功能设计

**7.1.1 数据库设计**

| ID   | 项目ID | 文件/文件夹名 | 类型        | 文件大小 | 父目录 | key    |
| ---- | ------ | ------------- | ----------- | -------- | ------ | ------ |
| 1    |        | xxx           | 1（文件）   | null     | null   | null   |
| 2    |        | xxxx          | 2（文件夹） | null     | 1      | 唯一值 |
| 3    |        | xxxxx         |             | null     | null   |        |

**7.1.2 数据库models设计**

```python
class FileRepository():
    ''' 文件库 '''
    project = models.ForeignKey(verbose_name='项目', to='project')
    file_type_choices = (
        (1, '文件'),
        (2, '文件夹')
    )
    file_type = models.SmallIntegerField(verbose_name='类型', choices=file_type_choices)
    name = models.CharField(verbose_name='文件夹名称', max_length=32, help_text="文件/文件夹名")
    key = models.CharField(verbose_name='文件存储在COS中的KEY', max_length=128, null=True, blank=True)
    file_size = models.IntegerField(verbose_name='文件大小', null=True, blank=True)
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)
    parent = models.ForeignKey(verbose_name='父级目录', to='self', related_name='child', null=True, blank=True)

    update_user = models.ForeignKey(verbose_name='最近更新者', to='UserInfo')
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)

```

**7.1.3 知识点**

**7.1.3.1 URL 传参/不传参**

```python
path('file/', manage.file, name='file')
# /file/
# /file?folder_id=50
def file(request.project_id):
    folder_id = request.GET.get('folder_id')
```

##### **7.2 bootstrap模态框+警告框**

##### **7.3 导航条**

```python
def file(request.project_id):
    folder_id = request.GET.get('folder_id')
    # 导航列表
    url_list = []
    if not folder_id:
        pass
    else:
        file_object = models.FileRepository.objects.filter(id=folder_id,file_type).first()
        row_object = file_object
        # 循环查找上一级文件夹名称
        while row_object:
            url_list.insert(0,{"id":row_object.id,"name":row_object.name)
            row_object = row_object.parent
            
    # 获取导航信息
    print(url_list)
```

##### **7.4 cos上传文件 js实现**

**7.4.1 下载js (前端的sdk)**

​	下载地址：`https://github.com/tencentyun/cos-js-sdk-v5/tree/master/dist`

```html
<script src="./cos-js-sdk-v5.min.js"></script>
```

**7.4.2 上传**

```html
{% load static %}
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <h1>示例1：直接通过秘钥进行上传文件</h1>
        <!-- multiple 表示多选 -->
        <input type="file" name="upload_file" id="uploadFile" multiple/>
        <script src="{% static 'js/jquery-3.4.1.min.js' %}"></script>
        <script src="{% static 'js/cos-js-sdk-v5.min.js' %}"></script>
        <script>
        var cos;
        $(function(){
            initCOS();
            bindChangeFileInput();
        });
            
        function initCOS(){
            cos = new COS({
                SecretID:'',
                SecretKey:'',
            });
        }
            
        function bindChangFileInput(){
            $('#uploadFile').change(function(){
                // 获取要上传的所有文件对象列表
                // $(this)[0] = document.getElementById('uploadFile')
                var files = $(this)[0].files;
                $.each(files, function(index,fileObject){
                    var fileName = fileObject.name;
                    // 上传文件
                    cos.putobject({
                        Bucket: 'xxxxx-1231231',
                        Region: 'ap-nanjing',
                        Key: fileName,
                        Body: fileObject, // 上传文件对象
                        onProgress: function(progressData){
                            // 进度条
                            console.log("文件上传进度--->",fileName,JSON.stringify(progressData));
                        }
                    }, function(err,data){
                        // 是否上传成功
                        console.log(err || data);
                    });
                })
            })
        }
        </script>
    </body>
</html>
```

**7.4.3 跨域问题(浏览器导致)**

1.对象存储返回值时，加上特殊响应头 `allow.origin:*`

2.腾讯对象存储设置 跨域访问CORS设置

| 来源Origin | 操作 Methods             | Allow-Headers | Expose-Headers | 超时 |
| ---------- | ------------------------ | ------------- | -------------- | ---- |
| *          | PUT,GET,POST,DELETE,HEAD | *             | -              | 0    |

**7.4.3 cos上传文件：临时秘钥【推荐】**

1. 路由

```python
path('demo2/', manage.demo2, name='demo2')
path('cos/credential/', manage.cos_credential, name='cos_credential')
```

2. 视图

```python
def demo2(request):
    return render(request,'demo2.html')

def cos_credential(request):
    # 生成一个临时凭证，并给前端返回
    # 1.安装一个生成临时凭证python模块 pip install -U qcloud-python-sts
    # 2.写代码
    from sts.sts import Sts
    config = {
        # 临时秘钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds':1800,
        # 固定秘钥 id
        'secret_id':"xxxxx",
        # 固定秘钥 key
        'secret_key':"xxxx",
        # 换成你的 bucket
        'bucket':"xxxxx-123123123",
        # 换成bucket所在地区
        'region':"ap-nanjing",
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录判断允许上传的具体路径
        # 例子：a.jpg 或者 a/* 或者 *（使用通配符*存在重大安全风险，请谨慎评估使用）
        'allow_prefix':'*',
        # 秘钥的权限列表，简单上传和分片需要以下的权限，其他权限列表请看
        # https://cloud.tencent.com/document/product/436/31923
        'allow_actions':[
            'name/cos:PostObject',
            # "*",
        ],
        
    }
    
    sts = Sts(config)
    result_dict = sts.get_credential()
    return = JsonResponse(result_dict)
```

3. html页面

```html
{% load static %}
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <h1>示例2：临时凭证上传文件</h1>
        <!-- multiple 表示多选 -->
        <input type="file" name="upload_file" id="uploadFile" multiple/>
        <script src="{% static 'js/jquery-3.4.1.min.js' %}"></script>
        <script src="{% static 'js/cos-js-sdk-v5.min.js' %}"></script>
        <script>
        var cos;
        $(function(){
            initCOS();
            bindChangeFileInput();
        });
            
        function initCOS(){
            cos = new COS({
                getAuthorization:function(options, callback){
                    // 向django后台发送请求，获取临时凭证
                    $.get('/cos/credential/',{
                        // 可从options取需要的参数
                    },function(data){
                        var credentials = data && data.credential;
                        if(!data || !credentials) return console.error('credentials invalid');
                        callback({
                            TmpSecretId: credentials.tmpSecretId,
                            TmpSecretKey: credentials.tmpSecretKey,
                            xCosSecurityToken: credentials.sessionToken,
                            StartTime: data.startTime,
                            ExpiredTime: data.expiredTime,
                        });
                    });
                }
            });
        }
            
        function bindChangFileInput(){
            $('#uploadFile').change(function(){
                // 获取要上传的所有文件对象列表
                // $(this)[0] = document.getElementById('uploadFile')
                var files = $(this)[0].files;
                $.each(files, function(index,fileObject){
                    var fileName = fileObject.name;
                    // 上传文件（异步）
                    cos.putobject({
                        Bucket: 'xxxxx-1231231',
                        Region: 'ap-nanjing',
                        Key: fileName,
                        Body: fileObject, // 上传文件对象
                        onProgress: function(progressData){
                            // 进度条
                            console.log("文件上传进度--->",fileName,JSON.stringify(progressData));
                        }
                    }, function(err,data){
                        // 是否上传成功
                        console.log(err || data);
                    });
                })
            })
        }
        </script>
    </body>
</html>
```

4. 浏览器跨域解决

1.对象存储返回值时，加上特殊响应头 `allow.origin:*`

2.腾讯对象存储设置 跨域访问CORS设置

| 来源Origin | 操作 Methods             | Allow-Headers | Expose-Headers | 超时 |
| ---------- | ------------------------ | ------------- | -------------- | ---- |
| *          | PUT,GET,POST,DELETE,HEAD | *             | -              | 0    |

5. 总结 采用方法

- python直接上传
- js + 临时凭证（跨域问题）

**7.3 cos的功能 & 项目**

1. 创建项目 & 创建存储桶

```python
# POST 对话框的ajax添加项目
# 获取新增项目的信息
form = ProjectModelForm(request, data=request.POST)
# 校验表单获取的数据
if form.is_valid():
    '''创建桶'''
    # 1.为项目创建一个桶 & 创建跨域规则
    name = form.cleaned_data['name']
    bucket = "{}-bucket-{}-1302952368".format( request.tracer.user.mobile_phone, str(int(time.time())))
    region = "ap-nanjing"

    creat_bucket(bucket, region)
    # 把桶和区域写到数据库

    # 2.创建项目
    form.instance.bucket = bucket
    form.instance.region = region
    form.instance.creator = request.tracer.user
    # 创建项目
    form.save()

    # 返回添加成功
    return JsonResponse({'status': True})

# 验证失败，返回错误数据
return JsonResponse({'status': False, 'error': form.errors})
```

```python
# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging
from django.conf import settings

def creat_bucket(bucket, region = "ap-nanjing"):
    '''
    :param bucket: 桶名称
    :param region: 区域
    :return:
    '''

    # 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # region = 'ap-nanjing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                               # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
    # token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
    # scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填


    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    # 创建桶
    client.create_bucket(
        Bucket=bucket,
        ACL="public-read",  # private / public-read / public-read-write
    )
    
    cors_config = {
        'CORSRule':[
            {
                'AllowedOrigin':'*', # ["https://www.qq.com",]
                'AllowedMethod':['GET','PUT','HEAD','POST','DELETE'],
                'AllowedHeader':"*", # ['x-cos-meta-test']
                'ExposeHeader':"*", # ['x-cos-meta-test1']
                'MaxAgeSeconds':500
            }
        ]
    }
    response = client.put_bucket_cors(
    	Bucket = bucket,
        CORSConfiguration = cors_config
    )
```

**7.5 markdown上传图片【无改动】**

**7.6 js上传文件**

- 临时凭证：当前项目的 桶 & 区域（request.tracer.project...）
- js上传文件：设置当前的 桶 & 区域

**7.7 this 知识点**

```javascript
var name = "123"
info = {
    name:"234",
    func:function(){
        console.log(this.name) # info.name > 234
        function test(){
            console.log(this.name) # window.name > 123
        }
        test()
    }
}
info.func()
```

总结：每个函数都是一个作用域，在他的内部都会存在this，谁调用的函数，函数里面this就是谁。

**7.8 闭包**

```javascript
data_list = [11,22,33];
for(var i=0;i++;i<data.length){
    function xx(data){
        $.ajax({
            url:".....",
            data:{value:data_list[data]},
            success:function(res){
                // 1分钟之后执行回调函数
                console.log(data); // 输出：0/1/2
            }
        })
    }
    xx(i)
}
console.log(i) // 输出：2
```

注意事项：循环内容发送异步请求，异步任务成功之后，通过闭包来解决。

**7.9 文件管理实现**

**7.9.1 创建文件管理**

> 思路：通过 GET，POST 判断是展示操作还是新建操作。通过url后面是否带有folder参数，判断展示路径
>
> 知识点：
>
> 加载后重新刷新页面
>
> ```javascript
> location.href = location.href;
> ```

```python
# POST 添加文件夹
    form = FolderModelForm(request, parent_object, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        # 往数据库添加文件夹
        form.save()
        return JsonResponse({'status': True})
```

前端

```html
<div class="panel-heading">
    <div>文件夹</div>
    <div>
        <a class="btn btn-success btn-xs" data-toggle="modal" data-target="#addModal" data-whatever="新建文件夹">
            <i class="fa fa-plus-circle" aria-hidden="true"></i> 新建文件夹
        </a>
    </div>
</div>
```

```javascript
var FOLDER_URL = "?folder=" + {{ request.tracer.project.id }}

    $(function (){
        initAddModal();
        bindModelSubmit();
    });
    
    function initAddModal() {
        $('#addModal').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget); // Button that triggered the modal
      var recipient = button.data('whatever'); // Extract info from data-* attributes
      var modal = $(this);
      modal.find('.modal-title').text(recipient);

      // 实现表示清空
      modal.find('.error-msg').empty();
      {#$('#form')[0].reset();#}
})
    }
    
    function bindModelSubmit() {
        $('#btnFormSubmit').click(function () {
            $.ajax({
                url:location.href,
                type:"POST",
                data:$("#form").serialize(), // 获取表单数据
                dataType:"JSON",
                success:function (res){
                    if(res.status){
                        location.href = location.href;
                    }else {
                        $.each(res.error, function (key, value) {
                            $("#id_" + key).next().text(value[0]);
                        })
                    }
                }
            })
        })
    }
```



**7.9.2 文件列表 & 进入文件夹**

**7.9.3 编辑文件夹**

> 思路：通过返回fid判断是否是新建文件夹 还是 修改文件夹名称

```python
fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.FileRepository.objects.filter(id=int(fid), file_type=2, project=request.tracer.project).first()

    if edit_object:
        # 编辑
        form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:
        # 添加
        form = FolderModelForm(request, parent_object, data=request.POST)

```

前端添加fid标签

```django
{% if item.file_type == 2 %}
<a class="btn btn-default btn-xs" data-toggle="modal"
   data-target="#addModal"
   data-whatever="编辑文件夹"
   data-name="{{ item.name }}"
   data-fid="{{ item.id }}"
   >
    <i class="fa fa-pencil-square-o" aria-hidden="true"></i>
    编辑
</a>
{% endif %}
```

```javascript
if (fid){
    // 编辑
    // name
    modal.find('#id_name').val(name);
    modal.find('#fid').val(fid);
}else {
    // 新建
    // 实现表示清空
    modal.find('.error-msg').empty();
    $('#form')[0].reset();
}
```



**7.9.4 删除文件夹（DB级联删除 & 删除cos文件）**

> 思路：通过模态对话框，添加fid属性，使用fid属性进行id传递，从而实现对应文件以及文件夹的删除

- 在数据库中删除

```javascript
// 对删除按钮属性信息进行编辑
$('#alertModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var fid = button.data('fid'); // Extract info from data-* attributes
    $('#btnDelete').attr('fid',fid)
})
```

```python
if delete_object.file_type == 1:
    # 删除文件（数据库文件删除，cos文件删除，项目已使用的空间容量返还）
    pass
else:
    # 删除文件夹（找到文件夹下所有的文件>数据库文件删除，cos文件删除，项目已使用的空间容量返还）
    pass
```

- cos桶删除

```python
# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = 'xxxxxx'
# 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140

secret_key = 'xxxx'
# 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140

region = 'ap-nanjing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

objects = {
    "Quiet": "true",
    "Object": [
        {"Key":"name1"},
        {"Key":"name2"}
    ]
}

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

client.delete_object(
    Bucket='tracerbucket-1302952368',
    Key=objects
)
```

**7.9.5 文件上传**

**7.9.5.1 上传按钮**

> 思路: input 标签 css 属性 opacity:0；隐藏。 

```javascript
<input type="file" multiple/>
```



**7.9.5.2 获取临时凭证 & 上传文件**

> 引用包：
>
> 1. [cos-js-sdk-v5.js](https://github.com/tencentyun/cos-js-sdk-v5)
>
> 2. 生成临时凭证python模块 pip install -U qcloud-python-sts
>
> 下载源码包 ： https://[pypi](https://so.csdn.net/so/search?q=pypi&spm=1001.2101.3001.7020).org/project/qcloud-python-sts/#files
>
> 对下载后的文件夹中 setup.py 文件中 第四行增加或者修改encoding为utf-8 编码。
>
> [腾讯云对象存储临时密钥qcloud-python-sts库安装失败解决办法](https://blog.csdn.net/kobe_okok/article/details/124834918)
>
> 要点：跨越添加
>
> 上传文件前：临时凭证
>
> - 全局：默认超时之后，自动再次去获取（官方推荐）
> - 局部：每次上传文件之前，进行临时凭证的获取。
>
> 

- 容量的限制

  - 单文件限制
  - 总容量限制

  注意：不合法，错误提示；合法 继续上传。

- 合法继续上传

> 扩展：ajax 向后台发送消息 

```
前端：
	$.ajax({
		···
		data:{name:11,age:122,xx:[11,22,33]}
	})
	$.post(url,data,callback)
django后台：
	request.POST
	request.POST.get('name')
```

```
# 使用JSON.stringfy序列化
前端：
	$.ajax({
		···
		data:JSON.stringfy{name:{k1:1,k2:666},xx:[11,22,[11,22]]}
	})
	$.post(url,data,callback)
django后台：
	request.body 接收
	json.loads(request.body.decode('utf-8'))
```

**7.9.5.3 右下角展示进度条**

- 创建一个div
- onProgress对进度条的完成的百分比进行更新

```javascript
// 克隆进度条模板
var tr = $('#progressTemplate').find('tr').clone();
tr.find('.name').text(fileName);
$('#progressList').append(tr);
```

```html
<!-- 进度条 -->
    <div id="uploadProgress" class="upload-progress hide">
        <div class="panel panel-primary">
        <div class="panel-heading"><i class="fa fa-cloud-upload" aria-hidden="true"></i> 上传进度</div>
        <table class="table">
            <tbody id="progressList">

            </tbody>
        </table>
        </div>
    </div>

    <div class="hide">
    <table id="progressTemplate">
        <tr>
            <td>
                <div class="name"></div>
                <div class="progress">
                    <div class="progress-bar progress-bar-success progress-bar-striped"
                    role="progressbar" aria-valuenow="0"
                    aria-valuemin="0"
                    aria-valuemax="100" style="width: 0;">
                        0%
                    </div>
                </div>
                <div class="progress-error"></div>
            </td>
        </tr>
    </table>
    </div>
```

**7.9.5.4 上传文件保存到数据库**

- 每上传一个文件就向后台发送一个成功的任务 ajax请求
- 数据校验
- 存入数据库

通过指针存入数据库

```python
instance = models.FileRepository.objects.create(**data_dict)
```



更新项目已使用空间

```python
 # 项目的已使用空间:更新 (data_dict['file_size'])
    request.tracer.project.use_space += data_dict['file_size']
    request.tracer.project.save()
```

添加成功后返回数据给前端

```python
 # 添加成功之后，获取到添加的那个对象
    result = {
        'id': instance.id,
        'name': instance.name,
        'file_size': instance.file_size,
        'username': instance.update_user.username,
        'datetime': instance.update_datetime.strftime("%Y年%m月%d日 %H:%M"),
        # 'file_type': instance.get_file_type_display()
    }
```



**7.9.5.5 点击下载**

```
浏览器          django
请求            HttpResponse(...) 文本：响应头
请求            render(...)       文本：响应头
请求			  ...				文件内容：响应头
```



```python
def download(request):
    # 打开文件，获取文件的内容
    with open('xxx.png', mode="rb") as f:
        data = f.read()
        
    response = HttpResponse(data)
    # 设置响应头
    response['Content-Disposition'] = "attachment; filename = xxx.png"
    return response
```



#### **8 删除项目**

- 数据库项目删除

- COS中桶删除（碎片文件）



#### 9 问题管理

##### 9.1 表结构设计

```
产品经理：功能 + 原型图
```

| ID   | 内容 | 标题 | 类型FK | 模块FK | 状态CH | 优先级CH | 指派 | 关注者 | 开始时间 | 截至时间 | 模式 | 父问题 |
| ---- | ---- | ---- | ------ | ------ | ------ | -------- | ---- | ------ | -------- | -------- | ---- | ------ |
|      |      |      |        |        |        |          |      |        |          |          |      |        |
|      |      |      |        |        |        |          |      |        |          |          |      |        |
|      |      |      |        |        |        |          |      |        |          |          |      |        |

| id   | 问题类型 | 项目ID |
| ---- | -------- | ------ |
| 1    | Bug      |        |
| 2    | 功能     |        |
| 3    | 任务     |        |

| id   | 模块            | 项目 |
| ---- | --------------- | ---- |
| 1    | 第一期 用户认证 |      |
| 2    | 第二期 任务管理 |      |
| 3    | 第三期 支付     |      |

表设计

```python
class Issues(models.Model):
    """ 问题 """
    project = models.ForeignKey(verbose_name='项目', to='Project')
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType')
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey(verbose_name='指派', to='UserInfo', related_name='task', null=True, blank=True)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_problems')

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject

class Module(models.Model):
    ''' 模块(里程碑) '''
    project = models.ForeignKey(verbose_name='项目', to='Project')
    title = models.CharField(verbose_name='模块名称',max_length=32)
    
    def __str__(self):
        return self.title
    
class IssuesType(models.Model):
    ''' 问题类型 例如：任务、功能、Bug '''
    title = models.CharField(verbose_name='类型名称',max_length=32)
    color = models.SmallIntegerField(verbose_name='颜色')
    project = models.ForeignKey(verbose_name='项目',to='Project')
    
    def __str__(self):
        return self.title
```
##### 9.2 新建问题展示列表

- 分页处理

##### 9.2.1 模态对话框

- 显示对话框
- 显示用户要填写的数据（表单）

日期选择插件：

- [bootstrap-datepicker]([bootstrap-datepicker — bootstrap-datepicker documentation](https://bootstrap-datepicker.readthedocs.io/en/latest/))

```javascript
<link rel="stylesheet" href="{% static 'plugin/bootstrap-datepicker-1.9.0-dist/css/bootstrap-datepicker.min.css' %}">

<script src={% static 'plugin/bootstrap-datepicker-1.9.0-dist/js/bootstrap-datepicker.min.js' %}></script>
<script src={% static 'plugin/bootstrap-datepicker-1.9.0-dist/locales/bootstrap-datepicker.zh-CN.min.js' %}></script>
    
```

选择框插件

- [bootstrap-select]([Bootstrap Select中文网](https://www.bootstrapselect.cn/))

> 需要在modelForm中添加属性

```html
<link rel="stylesheet" href="{% static 'plugin/bootstrap-select-1.13.9/dist/css/bootstrap-select.min.css' %}">


<script src={% static 'plugin/bootstrap-select-1.13.9/dist/js/bootstrap-select.min.js' %}></script>
<script src={% static 'plugin/bootstrap-select-1.13.9/dist/js/i18n/defaults-zh_CN.min.js' %}></script>
    
```

##### 9.2.2 添加问题

**数据初始化 和 合法性**



**添加数据**



**错误提示**



##### 9.3 问题列表

ajax + 添加 + 页面刷新

> 知识点: 通过 str.rjust补充项目标签
>
> rjust(长度，“补充元素”)

```python
@register.simple_tag()
def string_just(num):
    if num < 100:
        num = str(num).rjust(3, "0")

    return "#{}".format(num)
```

##### 9.4 自定义分页

> http://127.0.0.1:8000/manage/9/issues/?page=1

- 数据库获取数据
  - models.user.objects.all()[0:10]
  - ...

> 分页组件应用

- 显示页码
  - 点击当前访问的默认显示
  - 显示11个页面

```python
分页组件应用：
1. 在视图函数中
    queryset = models.Issues.objects.filter(project_id=project_id)
    page_object = Pagination(
        current_page=request.GET.get('page'),
        all_count=queryset.count(),
        base_url=request.path_info,
        query_params=request.GET
    )
    issues_object_list = queryset[page_object.start:page_object.end]

    context = {
        'issues_object_list': issues_object_list,
        'page_html': page_object.page_html()
    }
    return render(request, 'issues.html', context)
2. 前端
    {% for item in issues_object_list %}
        {{item.xxx}}
    {% endfor %}

     <nav aria-label="...">
        <ul class="pagination" style="margin-top: 0;">
            {{ page_html|safe }}
        </ul>
    </nav>
```



##### 9.5 编辑问题

> 知识点：target="_blank" 打开新的页面
>
> ```
> <a target="_blank">
> ```

- 回复



- 问题的变更
