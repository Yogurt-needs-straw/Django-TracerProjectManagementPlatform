from django.contrib import admin
from django.urls import path, re_path, include

from web.views import account, home, project, manage, wiki, file

app_name = 'web'

urlpatterns = [
    path('register/', account.register, name='register'),
    path('login_sms/', account.login_sms, name='login_sms'),
    path('login/', account.login, name='login'),
    path('image/code/', account.image_code, name='image_code'),
    path('send/sms/', account.send_sms, name='send_sms'),
    path('logout/', account.logout, name='logout'),
    path('index/', home.index, name='index'),

    # 项目管理
    path('project/list/', project.project_list, name='project_list'),

    # 添加星标
    # /project/star/my/1 # 我创建的
    # /project/star/join/1 # 我参与的
    path('project/star/<str:project_type>/<int:project_id>/', project.project_star, name='project_star'),

    # 取消星标
    path('project/unstar/<str:project_type>/<int:project_id>/', project.project_unstar, name='project_unstar'),

    # 进入项目管理
    # 使用路由分发
    path('manage/<int:project_id>/', include([
        path('dashboard/', manage.project_dashboard, name='dashboard'),
        path('issues/', manage.project_issues, name='issues'),
        path('statistics/', manage.project_statistics, name='statistics'),

        # wiki路径
        path('wiki/', wiki.project_wiki, name='wiki'),
        path('wiki/add/', wiki.wiki_add, name='wiki_add'),
        path('wiki/catalog/', wiki.catalog, name='wiki_catalog'),
        path('wiki/delete/<int:wiki_id>/', wiki.delete, name='wiki_delete'),
        path('wiki/edit/<int:wiki_id>/', wiki.edit, name='wiki_edit'),
        path('wiki/upload/', wiki.upload, name='wiki_upload'),

        # file 路径
        path('file/', file.file, name='file'),
        path('file/delete/', file.file_delete, name='file_delete'),

        path('setting/', manage.project_setting, name='setting'),
    ], None)),

]
