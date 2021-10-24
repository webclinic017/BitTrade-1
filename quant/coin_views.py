from datetime import datetime

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count

from bdd.settings import ActiveStrategies
from users.models import UserProfile
from .models import Ohlcv, Coin, Signal
from bdd.decorators import *

from quant.binance_spot.signals import open_order as open_binance_order
from quant.binance_spot.signals import close_order as close_binance_order

from bdd.config.binance_spot_coins import BinanceSpotCoins

from binance.client import Client as BinanceClient

@staff_member_required
def index(request):
    coins = Coin.objects.filter(open_trade=True).order_by('name')
    return render(request, 'quant/index.html', {'coins': coins})

@staff_member_required
def add(request, exchange, coin_id):
    coin = Coin.objects.get(pk=coin_id)
    strategy = coin.strategy
    strategy_code = strategy.code
    if strategy.coin_set.aggregate(Sum('position'))['position__sum'] < ActiveStrategies[strategy_code]['max_position']:
        binance_client = BinanceClient()
        order_book = binance_client.get_order_book(symbol=coin.spot_symbol, limit=5)
        coin.spot_price = float(order_book['asks'][-1][0]) #买价(Bid)、卖价(Ask)
        coin.position = coin.position + 1
        coin.save()
        open_binance_order(coin, strategy_code, coin.position, coin.spot_price, coin.spot_price)
    return HttpResponseRedirect("/q/"+exchange+"/strategies/"+strategy_code)

@staff_member_required
def close(request, exchange, coin_id):
    coin = Coin.objects.get(pk=coin_id)
    strategy_code = coin.strategy.code
    binance_client = BinanceClient()
    order_book = binance_client.get_order_book(symbol=coin.spot_symbol, limit=5)
    coin.spot_price = float(order_book['asks'][-1][0])
    coin.position = 0
    coin.save()
    close_binance_order(coin, strategy_code)

    #create_binance_signal(coin, 'close', 'long', coin.strategy.code, coin.spot_price, coin.spot_price)
    return HttpResponseRedirect("/q/"+exchange+"/strategies/"+strategy_code)


@staff_member_required
def minus(request, exchange, coin_id):
    coin = Coin.objects.get(pk=coin_id)
    close_binance_order(coin, coin.strategy.code, False)
    return HttpResponseRedirect("/q/"+exchange+"/strategies")


@staff_member_required
def toggle(request, exchange, id, direction):
    coin = Coin.objects.get(pk=id)
    coin.save()
    return HttpResponseRedirect("/q/"+exchange+"/coins")

@staff_member_required
def strategies(request, exchange='binance'):
    coins = Coin.objects.filter(exchange=exchange, open_trade=True).order_by('name')
    return render(request, 'quant/strategies.html', {'coins': coins, 'current_exchange': exchange, 'strategies': list(ActiveStrategies.keys())})

@staff_member_required
def signals(request, exchange='binance'):
    current_symbol = request.GET.get('symbol', None)
    current_strategy = request.GET.get('strategy', None)
    coins = Coin.objects.filter(exchange=exchange, open_trade=True).order_by('name')
    signal_list = Signal.objects.filter(exchange=exchange, strategy__isnull=False)
    if current_symbol and current_symbol:
        coin = Coin.objects.filter(exchange=exchange, symbol=current_symbol).first()
        signal_list = signal_list.filter(symbol=current_symbol)
    if current_strategy and current_strategy:
        signal_list = signal_list.filter(strategy=current_strategy)
    signal_list = signal_list.order_by('-update_time')
    paginator = Paginator(signal_list, 30)
    page = request.GET.get('page')
    signals = paginator.get_page(page)
    return render(request, 'quant/signals.html', {'current_symbol': current_symbol, 'current_strategy': current_strategy, 'current_exchange': exchange, 'strategies': list(ActiveStrategies.keys()), 'coins': coins, 'signals': signals})

@user_passes_test(lambda u: u.is_superuser)
def sync_orders(request, exchange, coin_id):
    coin = Coin.objects.get(pk=coin_id)
    users = UserProfile.objects.exclude(api_key__isnull=True).exclude(secret_key__isnull=True).filter(exchange='binance')
    for user in users:
        binance_client = BinanceClient(user.api_key, user.secret_key)
        trades = binance_client.get_my_trades(symbol=coin.spot_symbol, limit=100)
        if trades and not trades[-1]['isBuyer']:
            for trade in trades:
                order_time = datetime.fromtimestamp(trade['time']/1000)
                if order_time > user.date_joined:
                    order, created = user.order_set.get_or_create(trade_id=trade['id'])
                    if created:
                        order.price = trade['price']
                        order.volume = trade['qty']
                        order.commission = trade['commission']
                        order.symbol = coin.spot_symbol
                        order.total = trade['quoteQty']
                        order.direction = 'buy' if trade['isBuyer'] else 'sell'
                        order.created_at = order_time
                        order.save()
    coin.sync_time = datetime.now()
    coin.save()
    return HttpResponseRedirect("/q/"+exchange+"/strategies")
