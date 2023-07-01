import datetime
import json

from django.shortcuts import render, redirect
from django_redis import get_redis_connection

from utils.encrypt import uid
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
    _object = None
    if request.tracer.price_policy.category == 2:
        # 找到之前订单：总支付费用、开始~结束时间、剩余天数 = 抵扣的钱
        _object = models.Transaction.objects.filter(user=request.tracer.user, status=2).order_by('-id').first()
        total_timedelta = _object.end_datetime - _object.start_datetime
        balance_timedelta = _object.end_datetime - datetime.datetime.now()
        if total_timedelta.days == balance_timedelta.days:
            balance = _object.price / total_timedelta.days * (balance_timedelta.days - 1)
        else:
            balance = _object.price / total_timedelta.days * balance_timedelta.days

    if balance >= origin_price:
        return redirect('price')

    context = {
        'policy_id': policy_object.id,
        'number': number,
        'origin_price': origin_price,
        'balance': round(balance, 2),
        'total_price': origin_price - round(balance, 2),
    }

    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    conn.set(key, json.dumps(context), nx=60*30)

    context['policy_object'] = policy_object
    context['transaction'] = _object

    return render(request, 'web/payment.html', context)


def pay(request):
    ''' 生成订单 & 去支付宝支付 '''
    # 需要对用户提交的数据再次做校验
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)

    context_string = conn.get(key)
    if not context_string:
        return redirect('price')

    context = json.loads(context_string.decode('utf-8'))

    # 1.数据库中生成交易记录（待支付）
    # 等支付成功之后，我们需要把订单的状态更新为已支付，开始与结束时间
    order_id = uid(request.tracer.user.mobile_phone)
    models.Transaction.objects.create(
        status=1,
        order=order_id,
        user=request.tracer.user,
        price_policy_id=context['policy_id'],
        count=context['number'],
        price=context['total_price'],
    )

    # 2.跳转到支付宝支付
    # -生成一个支付宝连接
    # -跳转到这个链接
    url = "支付宝的支付链接"

    return redirect(url)

