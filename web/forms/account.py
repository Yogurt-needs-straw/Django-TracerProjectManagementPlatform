import random

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django import forms
from django_redis import get_redis_connection

from django_project_demo2 import settings
from utils.tencent.sms import send_sms_single
from web import models
from utils import encrypt
from web.forms.BootStrapForm import BootStrapForm


class RegisterModelForm(BootStrapForm, forms.ModelForm):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9})$', '手机号码格式错误'), ])
    password = forms.CharField(
        label='密码',
        # 密码长度限制
        min_length=6,
        max_length=64,
        error_messages={
          'min_length': "密码长度不能小于6个字符",
          'max_length': "密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput(attrs={'placeholder': "请输入密码"}))
    confirm_password = forms.CharField(
        label="重复密码",
        # 密码长度限制
        min_length=6,
        max_length=64,
        error_messages={
            'min_length': "重复密码长度不能小于6个字符",
            'max_length': "重复密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput(attrs={'placeholder': "请输入重复密码"}))
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput(attrs={'placeholder': "请输入验证码"})
    )

    class Meta:
        model = models.UserInfo
        fields = ["username", "email", "password", "confirm_password", "mobile_phone", "code"]

    # 校验用户名不能重复
    def clean_username(self):
        username = self.cleaned_data['username']

        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')

        return username

    # 校验邮箱名不能重复
    def clean_email(self):
        email = self.cleaned_data['email']

        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')

        return email

    # 密码获取后加密
    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密 & 返回
        return encrypt.md5(pwd)

    # 校验两次密码是否一致
    def clean_confirm_password(self):

        pwd = self.cleaned_data.get('password')
        confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_pwd:
            raise ValidationError('两次密码不一致')
        return confirm_pwd

    # 校验手机号
    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已注册')
        return mobile_phone

    # 验证code
    def clean_code(self):
        code = self.cleaned_data['code']

        # mobile_phone = self.cleaned_data['mobile_phone']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')

        redis_str_code = redis_code.decode('utf-8')

        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误，请重新输入')
        return code


class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9})$', '手机号码格式错误'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        '''手机号校验的钩子'''
        mobile_phone = self.cleaned_data['mobile_phone']

        # 判断短信模板是否有问题
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('短信模板错误')

        # 数据库中是否已有手机号
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()

        if tpl == 'login':
            # print(exists)
            if not exists:
                raise ValidationError('手机号不存在')
        else:
            # 校验数据库中是否已有手机号
            if exists:
                raise ValidationError('手机号已存在')

        # 发短信 & 写redis
        code = random.randrange(1000, 9999)

        # 发送短信
        sms = send_sms_single(mobile_phone, template_id, [code, ])
        if sms['result'] != 0:
            raise ValidationError("短信发送失败,{}".format(sms['errmsg']))

        # 验证码写入redis(django-redis)
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)


        return mobile_phone

class LoginSMSForm(BootStrapForm, forms.Form):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9})$', '手机号码格式错误'), ])

    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput(attrs={'placeholder': "请输入验证码"})
    )

    # 校验手机号
    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_object:
            raise ValidationError('手机号不存在')

        return user_object

    # 校验验证码
    def clean_code(self):
        code = self.cleaned_data['code']
        user_object = self.cleaned_data.get('mobile_phone')
        # 手机号不存在，验证码无需再校验
        if not user_object:
            return code
        # 创建redis连接
        conn = get_redis_connection()
        # 获取之前存入redis的code
        redis_code = conn.get(user_object.mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')

        redis_str_code = redis_code.decode('utf-8')

        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误，请重新输入')

        return code

class LoginForm(BootStrapForm,forms.Form):
    ''' 邮箱或手机号登录 '''

    '''forms.PasswordInput(render_value=True)
        render_value=True 保留上次输入的密码，默认为False不保留。
    '''
    username = forms.CharField(label='邮箱或手机号')
    password = forms.CharField(
        label='密码',
        # 密码长度限制
        min_length=6,
        max_length=64,
        error_messages={
            'min_length': "密码长度不能小于6个字符",
            'max_length': "密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput)
    code = forms.CharField(label='图片验证码')

    ''' 重写init方法，加入request '''
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    ''' 字段校验 '''
    ''' 密码 '''
    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密 & 返回
        return encrypt.md5(pwd)

    ''' 校验验证码 '''
    def clean_code(self):
        ''' 校验验证码是否正确 '''
        # 读取用户输入的验证码
        code = self.cleaned_data['code']

        # 获取session中获取验证码
        session_code = self.request.session.get('image_code')

        if not session_code:
            raise ValidationError('验证码已过期，请重新获取')

        '''用户输入的验证码与session中的验证码校对
            去除空格
            全部大写
        '''
        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError('验证码输入错误')

        return code
