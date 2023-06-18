from django.shortcuts import render


def statistics(request, project_id):
    ''' 统计页面 '''
    return render(request, 'statistics/statistics.html')

