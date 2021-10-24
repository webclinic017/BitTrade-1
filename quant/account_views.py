from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

from .models import Account, Order, Coin
from users.models import UserProfile
from bdd.decorators import *
from quant.okex_spot.signals import create_signal

@user_passes_test(lambda u: u.is_superuser)
def index(request, exchange):
    current_username = request.GET.get('username', None)
    users = UserProfile.objects.filter(api_key__isnull=False, secret_key__isnull=False)
    accounts = Account.objects.filter(margin_balance__isnull=False, margin_balance__gt=0.0001, user__api_key__isnull=False)
    if current_username:
        accounts = accounts.filter(user__username=current_username)
    accounts = accounts.order_by('-user_id', 'add_time')
    return render(request, 'quant/accounts.html', {'accounts': accounts, 'users': users, 'current_exchange': exchange})

@staff_member_required
def close(request, exchange, id, direction):
    account = Account.objects.get(pk=id)
    account.close_order(direction, True)
    return HttpResponseRedirect("/q/"+exchange+"/accounts")

@staff_member_required
def toggle(request, exchange, id):
    account = Account.objects.get(pk=id)
    account.save()
    return HttpResponseRedirect("/q/"+exchange+"/accounts")

@staff_member_required
def refresh(request, exchange, id):
    account = Account.objects.get(pk=id)
    symbol = account.symbol
    user = account.user
    if Coin.objects.filter(symbol=symbol).first():
        user.get_account(symbol)
    elif Coin.objects.filter(spot_symbol=symbol).first():
        user.get_spot_account(symbol)
    return HttpResponseRedirect("/q/"+exchange+"/accounts")

@user_passes_test(lambda u: u.is_superuser)
def orders(request, exchange):
    order_list = Order.objects.filter(symbol__isnull=False).order_by('-created_at', '-add_time')
    paginator = Paginator(order_list, 30)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    return render(request, 'quant/orders.html', {'orders': orders, 'current_exchange': exchange})
