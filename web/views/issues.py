from django.http import JsonResponse
from django.shortcuts import render

from web import models
from web.forms.issues import IssuesModelForm


def issues(request, project_id):
    if request.method == "GET":
        form = IssuesModelForm(request)

        issues_object_list = models.Issues.objects.filter(project_id=project_id)

        return render(request, 'issues/issues.html', {'form': form, 'issues_object_list': issues_object_list})

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

