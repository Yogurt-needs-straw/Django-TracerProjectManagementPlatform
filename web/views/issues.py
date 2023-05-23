import json

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from utils.encrypt import uid
from utils.pagination import Pagination
from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm, InviteModelForm


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成url
            # 在当前url的基础上增加一项
            query_dict = self.request.GET.copy()
            query_dict.mutable = True
            query_dict.setlist(self.name, value_list)

            # 剔除分页信息
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                # status=1&status=2
                url = "{}?{}".format(self.request.path_info, query_dict.urlencode())
            else:
                # 去除多余?号
                url = self.request.path_info

            tpl = "<a class=\"cell\" href=\"{url}\"><input type=\"checkbox\" {ck}/><label>{text}</label></a>"
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)

class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;'>")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            # 判断选择id
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成url
            # 在当前url的基础上增加一项
            query_dict = self.request.GET.copy()
            query_dict.mutable = True
            query_dict.setlist(self.name, value_list)

            # 剔除分页信息
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                # status=1&status=2
                url = "{}?{}".format(self.request.path_info, query_dict.urlencode())
            else:
                # 去除多余?号
                url = self.request.path_info

            html = "<option value='{url}' {selected}>{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)

        yield mark_safe("</select>")

def issues(request, project_id):
    if request.method == "GET":
        # 筛选条件（根据用户GET传参）
        # ?status=1&issues_type=1
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)  # 获取匹配到的值 [1,2]
            if not value_list:
                continue
            condition["{}__in".format(name)] = value_list
        '''
        condition = {
            "status__in":[1,2],
            "issues_type":[1],
        }
        '''

        # 分页获取数据  .filter(**condition)添加搜索条件
        queryset = models.Issues.objects.filter(project_id=project_id).filter(**condition)

        page_object = Pagination(
            # 获取请求页码
            current_page=request.GET.get('page'),
            # 获取数据总量
            all_count=queryset.count(),
            # url前缀
            base_url=request.path_info,
            # url
            query_params=request.GET,
            # 数据展示条数
            per_page=50,
        )

        issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)
        project_issues_type = models.IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')

        # 项目的创建者
        project_totlal_user = [(request.tracer.project.creator_id, request.tracer.project.creator.username,)]
        # 项目的参与者
        join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')
        project_totlal_user.extend(join_user)

        invite_form = InviteModelForm()

        context = {
            'form': form,
            'invite_form': invite_form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'filter_list': [
                {'title': "问题类型", 'filter': CheckFilter("issues_type", project_issues_type, request)},
                {'title': "状态", 'filter': CheckFilter("status", models.Issues.status_choices, request)},
                {'title': "优先级", 'filter': CheckFilter("priority", models.Issues.priority_choices, request)},
                {'title': "指派者", 'filter': SelectFilter("assign", project_totlal_user, request)},
                {'title': "关注者", 'filter': SelectFilter("attention", project_totlal_user, request)},

            ],
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
    if name == "attention":
        #
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': "数据格式错误"})

        if not value:
            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            # value=[1,2,3,4] -> id是否是项目成员(参与者、创建者)
            # 获取当前项目的所有成员
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username

            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在，请重新设置"})
                username_list.append(username)

            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name, ",".join(username_list))

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})


    # 2. 生成操作记录

    return JsonResponse({'status': False, 'error': "非法用户"})


def invite_url(request, project_id):
    """ 生成邀请码 """

    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1. 创建随机的邀请码
        2. 验证码保存到数据库
        3. 限制：只有创建者才能邀请
        """
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period', "无权创建邀请码")
            return JsonResponse({'status': False, 'error': form.errors})

        random_invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.project = request.tracer.project
        form.instance.code = random_invite_code
        form.instance.creator = request.tracer.user
        form.save()

        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('web:invite_join', kwargs={'code': random_invite_code})
        )

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    ''' 访问邀请码 '''


    return None