from django.shortcuts import render


def statistics(request):
    ''' 统计页面 '''
    return render(request, 'statistics/statistics.html')

