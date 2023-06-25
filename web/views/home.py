
from django.shortcuts import render

from web import models


def index(request):
    return render(request, 'web/index.html')


def price(request):
    ''' 套餐 '''

    # 获取套餐
    policy_list = models.PricePolicy.objects.filter(category=2)

    return render(request, 'web/price.html', {'policy_list': policy_list})


def payment(request):
    ''' 支付页面 '''
    return None