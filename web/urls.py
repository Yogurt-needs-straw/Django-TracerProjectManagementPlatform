from django.contrib import admin
from django.urls import path, re_path, include

from web.views import account, home, project, manage

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
        path('dashboard/', manage.project_dashboard, name='project_dashboard'),
        path('issues/', manage.project_issues, name='project_issues'),
        path('statistics/', manage.project_statistics, name='project_statistics'),
        path('file/', manage.project_file, name='project_file'),
        path('wiki/', manage.project_wiki, name='project_wiki'),
        path('setting/', manage.project_setting, name='project_setting'),
    ], None)),

]
