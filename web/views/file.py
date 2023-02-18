
from django.shortcuts import render

def file(requests, project_id):
    ''' 文件列表 '''
    return render(requests, 'file/file.html')

