import time

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from utils.tencent.cos import creat_bucket
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
                project_dic['star'].append({"value": row, "type": 'my'})
            else:
                project_dic['my'].append(row)

        # 获取用户参与的所有项目
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dic['star'].append({"value": item.project, "type": 'join'})
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
        '''创建桶'''
        # 为项目创建一个桶
        name = form.cleaned_data['name']
        bucket = "{}-{}-bucket-{}-1302952368".format(name, request.tracer.user.mobile_phone, str(int(time.time())))
        region = "ap-nanjing"

        creat_bucket(bucket, region)
        # 把桶和区域写到数据库
        # 验证通过: 项目名、颜色、项目描述、创建者(当前用户)

        form.instance.bucket = bucket
        form.instance.region = region
        # 创建者(当前用户)
        form.instance.creator = request.tracer.user

        # 创建项目
        instance = form.save()

        # 项目初始化问题类型
        issues_type_object_list = []
        # ["任务", "功能", "Bug"]
        for item in models.IssuesType.PROJECT_INIT_LIST:
            issues_type_object_list.append(models.IssuesType(project=instance, title=item))
        # print(issues_type_object_list)
        # 创建项目时添加IssuesType默认参数 project 和 title
        models.IssuesType.objects.bulk_create(issues_type_object_list)

        # 返回添加成功
        return JsonResponse({'status': True})

    # 验证失败，返回错误数据
    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    ''' 星标项目 '''
    # 我创建的项目星标
    if project_type == 'my':
        # 修改数据库中的数据
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)
        # 返回管理中心界面
        return redirect('/project/list')

    # 我参与的项目星标
    if project_type == 'join':
        # 修改数据库中的数据
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=True)
        # 返回管理中心界面
        return redirect('/project/list')

    return HttpResponse('请求错误')


def project_unstar(request, project_type, project_id):
    ''' 取消星标 '''
    # 我创建的项目取消星标
    if project_type == 'my':
        # 修改数据库中的数据
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=False)
        # 返回管理中心界面
        return redirect('/project/list')

    # 我参与的项目取消星标
    if project_type == 'join':
        # 修改数据库中的数据
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=False)
        # 返回管理中心界面
        return redirect('/project/list')

    return HttpResponse('请求错误')

