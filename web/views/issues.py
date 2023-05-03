import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from utils.pagination import Pagination
from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm


def issues(request, project_id):
    if request.method == "GET":
        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=project_id)

        page_object = Pagination(
            # 获取请求页码
            current_page=request.GET.get('page'),
            # 获取数据总量
            all_count=queryset.count(),
            # url前缀
            base_url=request.path_info,
            # url
            query_params=request.GET,
        )

        issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)
        context = {
            'form': form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html()
        }
        return render(request, 'issues/issues.html', context)

    # print(request.POST)
    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        # 添加默认信息
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user

        # 添加问题
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    ''' 编辑问题 '''

    # 表单默认信息填充
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

    form = IssuesModelForm(request, instance=issues_object)
    return render(request, 'issues/issues_detail.html', {'form': form, "issues_object": issues_object})

@csrf_exempt
def issues_record(request, project_id, issues_id):
    ''' 初始化操作记录 '''

    # 判断是否可以评论和是否可以操作这个问题


    if request.method == "GET":
        # print(issues_id)
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)

        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id,
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.tracer.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id,
        }

        return JsonResponse({'status': True, 'data': info})

    return JsonResponse({'status': False, 'error': form.errors})

@csrf_exempt
def issues_change(request, project_id, issues_id):

    # 获取当前操作的对象
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

    post_dict = json.loads(request.body.decode('utf-8'))
    ''' {'name': 'issues_type', 'value': '2'} 
        {'name': 'desc', 'value': '问题1123123'}
        {'name': 'status', 'value': '4'}
    '''
    name = post_dict.get('name')
    value = post_dict.get('value')
    # print(post_dict)
    field_object = models.Issues._meta.get_field(name)

    def create_reply_record(content):
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=change_record,
            creator=request.tracer.user,
        )
        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id,
        }
        return new_reply_dict

    # 1. 数据库字段更新
    # 1.1 文本
    if name in ["subject", "desc", "start_date", "end_date"]:
        if not value:
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            setattr(issues_object, name, None)
            issues_object.save()
            # 记录：xxx更新为了空 field_object.verbose_name
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            # 提交数据库保存
            setattr(issues_object, name, value)
            issues_object.save()
            # 记录：xxx更新为value
            change_record = "{}更新为{}".format(field_object.verbose_name, value)


        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # 1.2 FK字段（指派的话要判断是否创建者或者参与者）
    if name in ['issues_type', 'module', 'parent', 'assign']:
        # 用户选择为空
        if not value:
            # 不允许为空
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            # 允许为空
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)

        # 用户输入不为空
        else:
            if name == 'assign':
                # 是否是项目创建者
                if value == str(request.tracer.project.creator_id):
                    instance = request.tracer.project.creator
                else:
                # 是否是项目参与者
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id, user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None

                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})

                # 更新数据库
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = "{}更新为{}".format(field_object.verbose_name, str(instance))

            else:
                # 条件判断：用户输入的值，是自己的值。
                instance = field_object.remote_field.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})

                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = "{}更新为{}".format(field_object.verbose_name, str(instance))


        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # 1.3 choices字段
    if name in ['priority', 'status', 'mode']:
        selected_text = None

        for key, text in field_object.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': "您选择的值不存在"})

        setattr(issues_object, name, value)
        issues_object.save()
        change_record = "{}更新为{}".format(field_object.verbose_name, selected_text)

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # 1.4 M2M字段


    # 2. 生成操作记录

    return JsonResponse({})
