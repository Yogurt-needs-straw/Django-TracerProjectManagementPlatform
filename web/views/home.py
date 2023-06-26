
from django.shortcuts import render, redirect

from web import models


def index(request):
    return render(request, 'web/index.html')


def price(request):
    ''' 套餐 '''

    # 获取套餐
    policy_list = models.PricePolicy.objects.filter(category=2)

    return render(request, 'web/price.html', {'policy_list': policy_list})


def payment(request, policy_id):
    ''' 支付页面 '''

    # 1.价格策略（套餐）policy_id
    policy_object = models.PricePolicy.objects.filter(id=policy_id, category=2).first()
    if not policy_object:
        return redirect('price')

    # 2.要购买的数量
    number = request.GET.get('number', '')
    if not number or not number.isdecimal():
        return redirect('price')

    number = int(number)
    if number < 1:
        return redirect('price')

    # 3.计算原价
    origin_price = number * policy_object.price

    # 4.之前购买过套餐
    # 抵扣价格
    balance = 0
    if request.tracer.price_policy.category == 2:
        pass

    return None


