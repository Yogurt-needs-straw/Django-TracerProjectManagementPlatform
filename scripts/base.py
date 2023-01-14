''' 离线脚本 '''
''' 利用django配置文件 离线添加数据库信息 '''

import django
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project_demo2.settings")
django.setup()
