import datetime
import uuid

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.utils import timezone

from web import models
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSMSForm, LoginForm

''' 生成图片验证码 '''
from io import BytesIO
from utils.draw_code import check_code

# Create your views here.
def register(request):
    ''' 注册 '''
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'web/register.html', {'form': form})
    # print(request.POST)
    # 获取用户提交的数据
    form = RegisterModelForm(data=request.POST)
    # print(form.is_valid())
    if form.is_valid():
        # print(form.cleaned_data)
        # 验证通过，写入数据库(密码要是密文)
        # instance = form.save 在数据库中新增一条数据，并将新增的这条数据赋值给instance

        # 用户表中新增一条数据（注册）
        instance = form.save()

        # 创建交易记录
        # 方式一
        policy_object = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            user=instance,
            price_policy=policy_object,
            count=0,
            price=0,
            start_datetime=timezone.now()
        )

        # 方式二：什么都不需要写，使用默认的额度

        return JsonResponse({'status': True, 'data': '/login/'})

    return JsonResponse({'status': False, 'error': form.errors})

def send_sms(request):
    '''发送短信'''
    # print(request.GET)

    form = SendSmsForm(request, data=request.GET)
    # print(form)

    # 只是校验手机号：不能为空、格式是否正确
    print(form.is_valid())
    if form.is_valid():
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def login_sms(request):
    ''' 短信登录 '''
    if request.method == 'GET':
        form = LoginSMSForm()
        return render(request, 'web/login_sms.html', {'form': form})

    form = LoginSMSForm(request.POST)
    if form.is_valid():
        # 用户输入正确，登录成功
        user_object = form.cleaned_data['mobile_phone']
        print(user_object)

        # 用户信息放入session
        request.session['user_id'] = user_object.id
        request.session['user_name'] = user_object.username

        return JsonResponse({'status': True, 'data': '/index/'})
    return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    ''' 用户名和密码登录 '''

    if request.method == 'GET':
        '''传入request参数'''
        form = LoginForm(request)
        return render(request, 'web/login.html', {'form': form})

    '''传入request参数'''
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # 数据库中查询用户名和密码
        # user_object = models.UserInfo.objects.filter(username=username, password=password).first()

        # 通过邮箱和手机号判断用户
        # (手机=username and pwd=pwd) or (邮箱=username and pwd=pwd)
        user_object = models.UserInfo.objects.filter(Q(email=username) | Q(mobile_phone=username)).filter(
            password=password).first()

        # 判断
        if user_object:
           # 用户名密码正确
           # 登录成功

           request.session['user_id'] = user_object.id
           # 添加超时时间 两周
           request.session.set_expiry(60*60*24*14)

           return redirect('/index')
        form.add_error('username', '用户名或密码错误')

    return render(request, 'web/login.html', {'form': form})


def image_code(request):
    ''' 生成图片验证码 '''

    image_object, code = check_code()

    '''写入session'''
    request.session['image_code'] = code
    '''设置session超时时间,60秒后失效'''
    request.session.set_expiry(60)

    '''将图片写入内存'''
    stream = BytesIO()
    image_object.save(stream, 'png')

    return HttpResponse(stream.getvalue())


# 清空session数据
def logout(request):
    request.session.flush()
    return redirect('/index')


