from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web import models
from web.forms.wiki import WikiModelForm


def project_wiki(request, project_id):
    ''' wiki的首页 '''

    wiki_id = request.GET.get('wiki_id')
    # 判断wiki_id回传数据，是否仅是数字
    if (not wiki_id) or (not wiki_id.isdecimal()):
        # 如果带有字符串，返回首页
        return render(request, 'manage/wiki.html')

    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()

    return render(request, 'manage/wiki.html', {'wiki_object': wiki_object})


def wiki_add(request, project_id):
    ''' wiki添加 '''
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki/wiki_add.html', {'form': form})

    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
        # 判断用户是否已经选择了父文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.parent = 1

        form.instance.project = request.tracer.project
        form.save()
        url = reverse('web:wiki', kwargs={'project_id': project_id})
        # print(url)
        return redirect(url)

    return render(request, 'wiki/wiki_add.html', {'form': form})


def catalog(request, project_id):
    ''' 获取wiki目录 '''
    # 获取当前项目的文章目录 Queryset类型
    # .values 与 .values_list 返回数据类型不一样，.values返回的是字典数据类型，.values_list返回的是列表数据类型。
    data = models.Wiki.objects.filter(project=project_id).values("id", "title", "parent_id").order_by('depth', 'id')
    # 调用JsonResponse会自动使用json.dumps进行数据类型格式化，但是Queryset类型无法被格式化会报
    # GET http://127.0.0.1:8000/manage/5/wiki/catalog/ 500 (Internal Server Error)
    # 错误
    # 通过list转换成列表类型就可以了
    return JsonResponse({'status': True, 'data': list(data)})


# def detail(request, project_id):
#     ''' 文章详细页面查看
#         /detail?wiki_id=1
#      '''
#     return HttpResponse('查看文章详细')


def delete(request, project_id, wiki_id):
    ''' 删除文章 '''

    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()

    url = reverse('web:wiki', kwargs={'project_id': project_id})
    # print(url)
    return redirect(url)

