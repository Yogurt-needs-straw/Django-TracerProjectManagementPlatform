from django.shortcuts import render, redirect

from utils.tencent.cos import delete_bucket
from web import models


def setting(request, project_id):

    return render(request, 'setting/setting.html')

def delete(request, project_id):
    ''' 删除项目 '''

    if request.method == 'GET':
        return render(request, 'setting/delete.html')

    project_name = request.POST.get('project_name')

    if not project_name or project_name != request.tracer.project.name:
        return render(request, 'setting/delete.html', {'error': "项目名错误"})

    # 项目名写对了则删除(只有项目创建者可以删除)
    if request.tracer.user != request.tracer.project.creator:
        return render(request, 'setting/delete.html', {'error': "只有项目创建者可删除"})

    # 1.删除桶
    # -删除桶中的文件(找到桶中的所有文件 + 删除文件)
    # -删除桶中的碎片
    # -删除桶

    # 2.删除项目

    # 删除项目桶文件
    delete_bucket(request.tracer.project.bucket, request.tracer.project.region)

    # 删除数据库项目
    models.Project.objects.filter(id=request.tracer.project.id).delete()

    # 3.返回项目列表页
    return redirect("web:project_list")
