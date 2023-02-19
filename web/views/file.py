
from django.shortcuts import render
from web.forms.file import FolderModelForm

def file(requests, project_id):
    ''' 文件列表 '''
    form = FolderModelForm()
    return render(requests, 'file/file.html', {'form': form})

