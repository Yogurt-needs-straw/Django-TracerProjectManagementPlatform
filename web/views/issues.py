from django.http import JsonResponse
from django.shortcuts import render

from web.forms.issues import IssuesModelForm


def issues(request, project_id):
    if request.method == "GET":
        form = IssuesModelForm(request)

        return render(request, 'issues/issues.html', {'form': form})

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

