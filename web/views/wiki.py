from django.shortcuts import render


def project_wiki(request, project_id):

    return render(request, 'manage/wiki.html')

