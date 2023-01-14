from django.http import JsonResponse
from django.shortcuts import render

from web import models
from web.forms.project import ProjectModelForm


def project_list(request):
    ''' 项目列表 '''

    # # 获取当前的用户信息
    # print(request.tracer.user)
    # # 获取当前的策略信息
    # print(request.tracer.price_policy)

    if request.method == "GET":
        # GET请求查看项目列表
        '''
        1.从数据库中获取两部分数据
            我创建的所有项目：已星标、未星标
            我参与的所有项目：已星标、未星标
        2.提取已星标
            列表 = 循环[我创建的所有项目] + [我参与的所有项目] 把已星标的数据提取
            
        得到三个列表：星标、创建、参与
        '''
        project_dic = {'star': [], 'my': [], 'join': []}

        # 获取用户创建的所有项目
        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                project_dic['star'].append(row)
            else:
                project_dic['my'].append(row)

        # 获取用户参与的所有项目
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dic['star'].append(item.project)
            else:
                project_dic['join'].append(item.project)

        # 返回数据校验以及格式化
        form = ProjectModelForm(request)
        return render(request, 'project/project_list.html', {'form': form, 'project_dict': project_dic})

    # POST 对话框的ajax添加项目
    # 获取新增项目的信息
    form = ProjectModelForm(request, data=request.POST)
    # 校验表单获取的数据
    if form.is_valid():
        # 验证通过: 项目名、颜色、项目描述、创建者(当前用户)
        # 创建者(当前用户)
        form.instance.creator = request.tracer.user
        # 创建项目
        form.save()

        # 返回添加成功
        return JsonResponse({'status': True})

    # 验证失败，返回错误数据
    return JsonResponse({'status': False, 'error': form.errors})

