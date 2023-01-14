import random

from django.core.validators import RegexValidator
from django.shortcuts import render, HttpResponse

from django_project_demo2 import settings
from utils.tencent.sms import send_sms_single

# Create your views here.
def send_sms(request):
    '''发送短信
        ?tpl = login -> 5555
        ?tpl = login -> 6666
    '''
    phone_num = request.GET.get('phone_num')
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if not template_id:
        pass
        # return HttpResponse("模板不存在")

    code = random.randrange(1000, 9999)
    # res = send_sms_single('11000000000', template_id, [code, ])
    # #print(rst)
    # if res['result'] == 0:
    #     return HttpResponse('成功')
    # else:
    #     return HttpResponse(res['errmsg'])

    return HttpResponse("测试反馈")


from django import forms
from app01 import models

class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9})$', '手机号码格式错误'), ])
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'placeholder': "请输入密码"}))
    confirm_password = forms.CharField(
        label="重置密码",
        widget=forms.PasswordInput(attrs={'placeholder': "请输入重复密码"}))
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput(attrs={'placeholder': "请输入验证码"})
    )

    class Meta:
        model = models.UserInfo
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)

def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form': form})
