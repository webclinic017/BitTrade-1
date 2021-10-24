import os
import json
import requests
import math
from django.utils import timezone
from datetime import datetime, timedelta, date
from users.models import UserProfile
from quant.models import Coin, Signal, CoinPosition, Strategy
from bdd.settings import ActiveStrategies
from binance.client import Client as BinanceClient
from quant.tasks import sync_orders, sync_spot_account

def format_step(coin, quantity):
    if coin.spot_symbol == 'VETUSDT':
        return int(quantity/10)*10
    elif coin.qty_size:
        qty_size = coin.qty_size
        return math.floor(float(quantity)*qty_size) / qty_size
    else:
        return 0

def cancel_order(coin, strategy, direction):
    try:
        users = coin.userprofile_set.filter(exchange='binance').distinct()
        for user in users:
            binance_client = BinanceClient(user.api_key, user.secret_key)
            open_orders = binance_client.get_open_orders(symbol=coin.spot_symbol)
            for order in open_orders:
                if order['side'] == direction:
                    binance_client.cancel_order(symbol=coin.spot_symbol, orderId=order['orderId'])
    except Exception as error:
        send_notification(strategy, "{} 取消订单接口异常: {}".format(coin.spot_symbol, str(error)))

def open_order(coin, strategy, total_leverage, avg_price, best_price=None):
    symbol = coin.spot_symbol
    price = coin.spot_price
    users = coin.userprofile_set.filter(exchange='binance', usdt_unit__gt=0).order_by('usdt_unit').distinct()
    result = None
    units = ActiveStrategies[strategy]['units']
    base_unit = ActiveStrategies[strategy]['base']
    max_position = ActiveStrategies[strategy]['max_position']
    for user in users:
        try:
            binance_client = BinanceClient(user.api_key, user.secret_key)
            volume = 0

            #{1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 4, 7: 3, 8: 2, 9: 1}
            margin = user.usdt_unit #* units[total_leverage] if total_leverage <= max_position else user.usdt_unit

            total_balance = binance_client.get_asset_balance(base_unit)
            if total_balance and user.usdt_unit > 0:
                free_balance = float(total_balance['free'])

                if free_balance >= margin:
                    volume = format_step(coin, margin/price)
                elif free_balance >= user.usdt_unit:
                    volume = format_step(coin, free_balance/price)
                if best_price:
                    price = best_price
                if volume > 0:
                    result = binance_client.order_limit_buy(symbol=symbol, quantity=volume, price=str(price))

        except Exception as error:
            send_notification(strategy, "{} {} {} {} 开仓错误: {}".format(user.username, symbol, str(volume), str(price), str(error)))

    if result:
        send_notification(strategy, "{} 实盘买入: {} 当前价格: {} 总体均价 {} 开仓次数 {}".format(strategy, coin.name, str(coin.spot_price), str(avg_price), str(total_leverage)))

def close_order(coin, strategy, flush=True):
    symbol = coin.spot_symbol
    price = coin.spot_price
    users = coin.userprofile_set.filter(exchange='binance', usdt_unit__gt=0).order_by('usdt_unit').distinct()
    result = None
    for user in users:
        try:
            binance_client = BinanceClient(user.api_key, user.secret_key)
            asset_balance = binance_client.get_asset_balance(coin.name)
            volume = 0
            if asset_balance:
                total_volume = format_step(coin, float(asset_balance['free']))
                volume = total_volume
                if volume > 1/coin.qty_size:
                    result = binance_client.order_market_sell(symbol=symbol, quantity=volume)
        except Exception as error:
            send_notification(strategy, "{} {} {} 平仓错误: {}".format(user.username, symbol, str(price), str(error)))
    if result:
        text = "{} 实盘卖出: {} 价格 {}".format(strategy, coin.name, str(coin.spot_price))
        send_notification(strategy, text)

def add_more(coin, strategy, direction, close_price, add_size=0.97):
    try:
        symbol = coin.spot_symbol
        max_position = ActiveStrategies[strategy]['max_position']
        signal = Signal.objects.filter(symbol=symbol, direction=direction, exchange='binance', strategy=strategy).order_by('-update_time').first()
        if signal and signal.action == 'open' and signal.direction == 'long' and 0 < coin.position < max_position:
            if add_size > 0 and close_price < signal.last_price*add_size:
                avg_price = (signal.price + close_price) / 2
                total_leverage = coin.position + 1
                now = datetime.now()
                signal.update_time = now
                signal.price = avg_price
                signal.last_price = close_price
                signal.leverage = total_leverage#设置杠杆需要放在均价后面
                signal.save()

                coin.position = total_leverage
                coin.save()
                if coin.position >= coin.start_position:
                    open_order(coin, strategy, total_leverage, avg_price, coin.sell_price)

    except Exception as error:
        send_notification(strategy, "{} v3加仓接口异常: {}".format(symbol, str(error)))
        print(symbol + "v3加仓接口错误: " + str(error))

def stop_win(coin, strategy, direction, close_price, win):
    try:
        symbol = coin.spot_symbol
        signal = Signal.objects.filter(symbol=symbol, direction=direction, exchange='binance', strategy=strategy).order_by('-update_time').first()
        if signal and signal.action == 'open' and win > 0:
            if close_price > signal.price*(1+win):
                create_signal(coin, strategy, 'close', 'long', close_price)

    except Exception as error:
        send_notification(strategy, "{} 主动止盈接口异常: {}".format(symbol, str(error)))
        print(symbol + "主动止盈错误: " + str(error))

def create_signal(coin, strategy, action, direction, close_price):
    try:
        symbol = coin.spot_symbol
        signal = Signal.objects.filter(symbol=symbol, direction=direction, exchange='binance', strategy=strategy).order_by('-update_time').first()
        if action == 'open':
            total_leverage = 1
            if (signal is None or signal.action != action):
                Signal.objects.create(coin=coin, last_price=close_price, price=close_price, leverage=total_leverage, symbol=symbol, direction=direction, action=action, exchange='binance', strategy=strategy)
                coin.status = 1
                coin.position = total_leverage
                coin.save()
                if coin.position >= coin.start_position:
                    open_order(coin, strategy, total_leverage, close_price, close_price)

        elif action == 'close':
            if direction == 'long':
                if signal is not None and signal.action == 'open':
                    close_order(coin, strategy)
                    new_signal = Signal.objects.create(coin=coin, symbol=symbol, direction=direction, action=action, leverage=signal.leverage, price=coin.spot_price, exchange='binance', strategy=strategy)
                    gap = new_signal.price - signal.price
                    new_signal.profit = gap/signal.price
                    new_signal.save()
                    cancel_order(coin, strategy, 'BUY')
                    coin.status = 0
                    coin.position = 0
                    coin.save()
                    sync_orders.apply_async((coin.id,), countdown=120)
    except Exception as error:
        send_notification(strategy, "{} 现货信号接口异常: {}".format(symbol, str(error)))
        print(symbol + "现货信号错误: " + str(error))

def send_notification(strategy_code, text=''):
    strategy = Strategy.objects.filter(code=strategy_code).first()
    if strategy and strategy.push_url:
        headers = {'Content-type': 'application/json'}
        data = {
            "msgtype": "markdown",
            "markdown":
                {
                    "title": '新提醒',
                    "text": text
                },
            "at": {"isAtAll": True}
        }
        if os.uname()[0] != 'Darwin':
            requests.post(strategy.push_url, json=data, headers=headers)
