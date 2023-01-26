from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web import models
from web.forms.wiki import WikiModelForm


def project_wiki(request, project_id):

    return render(request, 'manage/wiki.html')


def wiki_add(request, project_id):
    ''' wiki添加 '''
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki/wiki_add.html', {'form': form})

    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
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
    data = models.Wiki.objects.filter(project=project_id).values("id", "title", "parent_id")
    # 调用JsonResponse会自动使用json.dumps进行数据类型格式化，但是Queryset类型无法被格式化会报
    # GET http://127.0.0.1:8000/manage/5/wiki/catalog/ 500 (Internal Server Error)
    # 错误
    # 通过list转换成列表类型就可以了
    return JsonResponse({'status': True, 'data': list(data)})


