import json

import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.urls import reverse

from utils.tencent.cos import delete_file, delete_file_list, credential
from web import models
from web.forms.file import FolderModelForm, FileModelForm

from django.views.decorators.csrf import csrf_exempt

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
            'folder_object': parent_object,
        }
        return render(request, 'file/file.html', context)

    # POST 添加文件夹 & 文件夹的修改
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

    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        # 往数据库添加文件夹
        form.save()
        return JsonResponse({'status': True})


    return JsonResponse({'status': False, 'error': form.errors})


# http://127.0.0.1:8000/manage/1/file/delete/?fid=1
def file_delete(request, project_id):
    ''' 删除文件 '''

    fid = request.GET.get('fid')

    # 删除文件 & 文件夹（级联删除）
    delete_object = models.FileRepository.objects.filter(id=fid, project=request.tracer.project).first()
    if delete_object.file_type == 1:
        # 字节
        # 删除文件,将容量还给当前项目的已使用空间
        request.tracer.project.use_space -= delete_object.file_size
        request.tracer.project.save()

        # cos中删除文件
        delete_file(request.tracer.project.bucket, request.tracer.project.region, delete_object.key)

        # 数据库中删除当前文件
        delete_object.delete()

        return JsonResponse({'status': True})


    # 删除文件夹（找到文件夹下所有的文件>数据库文件删除，cos文件删除，项目已使用的空间容量返还）
    # delete_object
    # 要返还的文件大小
    total_size = 0
    # 要删除文件夹列表
    folder_list = [delete_object]
    # cos桶key
    key_list = []
    for folder in folder_list:
        child_list = models.FileRepository.objects.filter(project=request.tracer.project, parent=folder).order_by('-file_type')
        for child in child_list:
            if child.file_type == 2:
                # 为文件夹
                folder_list.append(child)
            else:
                # 文件
                # 文件大小
                total_size += child.file_size
                # 删除文件
                key_list.append({"key": child.key})

    # cos 批量删除文件
    if key_list:
        delete_file_list(request.tracer.project.bucket, request.tracer.project.region, key_list)

    # 归还容量
    if total_size:
        request.tracer.project.use_space -= total_size
        request.tracer.project.save()

    # 数据库中删除当前文件
    delete_object.delete()

    return JsonResponse({'status': True})

# 免除csrf认证
@csrf_exempt
def cos_credential(request, project_id):
    ''' 获取cos上传的临时凭证 '''
    # 用户单容量范围
    per_file_limit = request.tracer.price_policy.per_file_size * 1024 * 1024
    # 当项目空间
    total_file_limit = request.tracer.price_policy.project_space * 1024 * 1024 *1024

    total_size = 0

    file_list = json.loads(request.body.decode('utf-8'))
    # print(file_list)
    # 获取要上传的每个文件 & 文件大小
    for item in file_list:
        # 文件的字节大小 item['size'] = B
        # 单文件限制的大小 M
        # 超出限制
        if item['size'] > per_file_limit:
            msg = "单文件超出限制（最大{}M），文件：{}".format(request.tracer.price_policy.per_file_size,item['name'])
            return JsonResponse({'status': False, 'error': msg})
        total_size += item['size']

    # 总容量限制
    # 项目的允许的空间
    # project_space = request.tracer.price_policy.project_space
    # 项目已使用的空间
    project_use_space = request.tracer.project.use_space

    if project_use_space + total_size > total_file_limit:
        return JsonResponse({'status': False, 'error': '容量超过限制，请升级套餐。'})

    # 做容量限制：单文件 & 总容量
    data_dict = credential(request.tracer.project.bucket, request.tracer.project.region)
    # print(data_dict)
    return JsonResponse({'status': True, 'data': data_dict})

# 免除csrf认证
@csrf_exempt
def file_post(request, project_id):
    ''' 已上传成功的文件写入到数据 '''
    '''
    name:fileName,
    key:key ,
    size:fileSize,
    parent: CURRENT_FOLOER_ID,
    etag: data.ETag,
    file_path:data.Location,
    '''
    # print(request.POST)

    # 根据key再去cos获取文件ETag和前端传过来的ETag校验

    # 把获取到的数据写入数据库即可
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验成功 将数据写入数据库

        # 通过modelForm.save 存储到数据库中的数据数据返回的instance对象，无法通过get_xx_display获取chioce的中文
        # form.instance.file_type = 1
        # form.update_user = request.tracer.user
        # instance = form.save()

        # 选择该方式添加数据库数据
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({
            'project': request.tracer.project,
            'file_type': 1,
            'update_user': request.tracer.user,
        })
        instance = models.FileRepository.objects.create(**data_dict)

        # 项目的已使用空间:更新 (data_dict['file_size'])
        request.tracer.project.use_space += data_dict['file_size']
        request.tracer.project.save()

        # 添加成功之后，获取到添加的那个对象
        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime("%Y年%m月%d日 %H:%M"),
            'download_url': reverse('web:file_download', kwargs={"project_id": project_id, 'file_id': instance.id}),
            # 'file_type': instance.get_file_type_display()
        }

        return JsonResponse({'status': True, 'data': result})

    return JsonResponse({'status': False, 'data': "文件错误"})


def file_download(request, project_id, file_id):
    ''' 下载文件 '''

    # 文件内容
    # 响应头
    # 打开文件，获取文件的内容

    # 数据库查询该文件访问url
    file_object = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()

    res = requests.get(file_object.file_path)
    data = res.content

    response = HttpResponse(data)
    # 设置响应头
    response['Content-Disposition'] = "attachment; filename={}".format(file_object.name)

    return response

