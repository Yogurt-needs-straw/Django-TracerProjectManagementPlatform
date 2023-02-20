
from django.shortcuts import render
from django.http import JsonResponse

from web import models
from web.forms.file import FolderModelForm

def file(request, project_id):
    ''' 文件列表 & 添加文件夹 '''
    if request.method == "GET":
        form = FolderModelForm()
        return render(request, 'file/file.html', {'form': form})

    # 获取父级文件夹
    parent_object = None
    folder_id = request.GET.get('folder', "")  # 如果有值获取folder 如果没有值为空
    # 判断是否是十进制的值
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2, project=request.tracer.project).first()

    # 添加文件夹
    form = FolderModelForm(request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        # 往数据库添加文件夹
        form.save()
        return JsonResponse({'status': True, 'error': form.errors})


    return JsonResponse({'status': False, 'error': form.errors})
