from django.shortcuts import render, redirect
from django.urls import reverse

from web.forms.wiki import WikiModelForm


def project_wiki(request, project_id):

    return render(request, 'manage/wiki.html')


def wiki_add(request, project_id):
    ''' wiki添加 '''
    if request.method == 'GET':
        form = WikiModelForm()
        return render(request, 'wiki/wiki_add.html', {'form': form})

    form = WikiModelForm(request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('web:wiki', kwargs={'project_id': project_id})
        # print(url)
        return redirect(url)

    return render(request, 'wiki/wiki_add.html', {'form': form})
