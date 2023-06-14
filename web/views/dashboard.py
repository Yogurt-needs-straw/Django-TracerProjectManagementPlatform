import collections
import datetime
import time

from django.db.models import Count
from django.http import JsonResponse
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


    # 项目成员
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values('user_id', 'user__username')

    # 最近的10个问题
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]

    context = {
        'status_dict': status_dict,
        'user_list': user_list,
        'top_ten': top_ten,
    }

    return render(request, 'dashboard/dashboard.html', context)


def issues_chart(request, project_id):
    ''' 在概览页面生成highcharts所需要的数据 '''

    # 当前时间
    today = datetime.datetime.now().date()

    # 最近30天，每天创建的问题数据量
    '''
        { 
            2020-03-31:[123123123112312,0],
            2020-03-31:[123123123112313,0],
        }
        '''
    date_dict = collections.OrderedDict()
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)
        date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

    # 去数据中查询最近30天的所有的数据 & 根据日期进行每天分组


    # select id,name,email from table;
    # select id,name, 1 as f from table;

    result = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=today-datetime.timedelta(days=30)).extra(
        select={'ctime': "strftime('%%Y-%%m-%%d',web_issues.create_datetime)"}).values('ctime').annotate(ct=Count('id'))
    # print(result)

    for item in result:
        date_dict[item['ctime']][1] = item['ct']



    return JsonResponse({'status': True, 'data': list(date_dict.values())})


