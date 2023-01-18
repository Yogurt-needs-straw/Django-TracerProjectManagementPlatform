from django.shortcuts import render


def project_dashboard(request, project_id):

    return render(request, 'manage/dashboard.html')


def project_issues(request):

    return render(request, 'manage/issues.html')


def project_statistics(request):

    return render(request, 'manage/statistics.html')


def project_file(request):

    return render(request, 'manage/file.html')


def project_wiki(request):

    return render(request, 'manage/wiki.html')


def project_setting(request):

    return render(request, 'manage/setting.html')
