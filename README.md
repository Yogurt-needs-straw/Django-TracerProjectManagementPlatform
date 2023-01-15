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

