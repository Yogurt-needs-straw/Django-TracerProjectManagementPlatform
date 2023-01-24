
from django.template import Library
from django.urls import reverse

from web import models

register = Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    ''' 菜单栏项目列表 '''
    # 1.获取创建的所有项目
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)

    # 2.获取参与的所有项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)

    return {"my": my_project_list, "join": join_project_list, "request": request}

''' 项目菜单栏默认选中 '''
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

    # 添加active属性
    for item in data_list:
        # item['url']
        # 当前用户访问的url：request.path_info
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'

    return {'data_list': data_list}
