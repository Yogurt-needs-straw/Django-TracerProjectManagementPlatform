from django.http import JsonResponse
from django.shortcuts import render

from utils.pagination import Pagination
from web import models
from web.forms.issues import IssuesModelForm


def issues(request, project_id):
    if request.method == "GET":
        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=project_id)

        page_object = Pagination(
            # 获取请求页码
            current_page=request.GET.get('page'),
            # 获取数据总量
            all_count=queryset.count(),
            # url前缀
            base_url=request.path_info,
            # url
            query_params=request.GET,
        )

        issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)
        context = {
            'form': form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html()
        }
        return render(request, 'issues/issues.html', context)

    # print(request.POST)
    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        # 添加默认信息
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user

        # 添加问题
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    ''' 编辑问题 '''

    # 表单默认信息填充
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

    form = IssuesModelForm(request, instance=issues_object)
    return render(request, 'issues/issues_detail.html', {'form': form})


def issues_record(request, project_id, issues_id):
    ''' 初始化操作记录 '''
    reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)

    # 将queryset转换为json格式
    data_list = []
    for row in reply_list:
        data = {
            'id': row.id,
            'reply_type_text': row.get_reply_type_display(),
            'content': row.content,
            'creator': row.creator.username,
            'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': row.reply_id,
        }
        data_list.append(data)

    return JsonResponse({'status': True, 'data': data_list})

