
from django.shortcuts import render
from django.http import JsonResponse

from web import models
from web.forms.file import FolderModelForm

def file(request, project_id):
    ''' 文件列表 & 添加文件夹 '''
    # 获取父级文件夹
    parent_object = None
    folder_id = request.GET.get('folder', "")  # 如果有值获取folder 如果没有值为空
    # 判断是否是十进制的值
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.tracer.project).first()
    # GET 查看页面
    if request.method == "GET":

        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent

        # 当前目录下所有的文件和文件夹获取到
        queryset = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            # 进入目录
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            # 跟目录
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        form = FolderModelForm(request, parent_object)

        context = {
            'form': form,
            "file_object_list": file_object_list,
            "breadcrumb_list": breadcrumb_list,
        }
        return render(request, 'file/file.html', context)

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


    return JsonResponse({'status': False, 'error': form.errors})
