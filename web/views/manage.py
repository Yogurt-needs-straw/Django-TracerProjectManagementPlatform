from django.shortcuts import render


# def project_dashboard(request, project_id):
#
#     return render(request, 'manage/dashboard.html')


def project_issues(request, project_id):

    return render(request, 'manage/issues.html')


def project_statistics(request, project_id):

    return render(request, 'manage/statistics.html')


# def project_file(request, project_id):
#
#     return render(request, 'manage/files.html')
