import collections

from django.db.models import Count
from django.shortcuts import render

from web import models


def dashboard(request, project_id):
    ''' 概览 '''

    # 问题数据处理
    status_dict = collections.OrderedDict()
    for key, text in models.Issues.status_choices:
        status_dict[key] = {'text': text, 'count': 0}

    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))

    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    context = {
        'status_dict': status_dict
    }

    return render(request, 'dashboard/dashboard.html', context)


