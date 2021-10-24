import os
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Avg, Count, Min, Sum
import pandas as pd
import json
import random
import requests
import quant.indicators as indicators
import pandas_ta as ta
from quant.models import Coin, Ohlcv
from users.models import UserProfile
from binance.client import Client as BinanceClient
from bdd.config.binance_spot_coins import BinanceSpotCoins

logger = get_task_logger(__name__)
connect_timeout, read_timeout = 5.0, 30.0

def get_ohlcvs(exchange, symbol):
    if exchange == 'binance':
        ohlcv_15m = Ohlcv.objects.get(exchange=exchange, symbol=symbol, period='15min')
        #ohlcv_15m = Ohlcv.objects.get(exchange=exchange, symbol=symbol, period='15min')
        #ohlcv_30m = Ohlcv.objects.get(exchange=exchange, symbol=symbol, period='30min')
        #ohlcv_1h = Ohlcv.objects.get(exchange=exchange, symbol=symbol, period='1hour')
        ohlcvs = [ohlcv_15m]
        return ohlcvs
    elif exchange == 'dc':
        ohlcv_5m = Ohlcv.objects.get(exchange=exchange, symbol=symbol, period='5min')
        return [ohlcv_5m]
    return []

def get_df(ohlcv):
    df = ohlcv.get_df()
    df = indicators.supertrend(df, 14, 4)
    df['rsi6'] = df.ta.rsi(length=6)
    df['rsi12'] = df.ta.rsi(length=12)
    #df['macds'] = df.ta.macd()['MACDS_12_26_9']
    #df['macd_rsi12'] = indicators.rsi_rma(df, length=12, close='macd')#
    #supertrend = df.ta.supertrend(length=14, multiplier=4)
    #df['dir'] = supertrend['SUPERTd_14_4.0']
    return df

@shared_task(bind=True, max_retries=1)
def sync_orders(self, coin_id):
    coin = Coin.objects.get(pk=coin_id)
    users = coin.userprofile_set.filter(exchange__in=['binance', 'binance_etf']).order_by('usdt_unit').distinct()
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

@shared_task(bind=True, max_retries=1)
def sync_spot_account(self, coin_id):
    coin = Coin.objects.get(pk=coin_id)
    users = coin.userprofile_set.filter(exchange__in=['binance', 'binance_etf']).order_by('usdt_unit').distinct()
    for user in users:
        try:
            binance_client = BinanceClient(user.api_key, user.secret_key)
            asset_balance = binance_client.get_asset_balance(coin.name)
            if asset_balance:
                account, created = user.account_set.get_or_create(symbol=coin.name)
                if asset_balance['locked']:
                    account.margin_frozen = round(float(asset_balance['locked']), 4)
                if asset_balance['free']:
                    account.margin_available = round(float(asset_balance['free']), 4)
                    account.margin_balance = round((account.margin_frozen+account.margin_available) * float(coin.spot_price), 4)
                if user.spot_asset and user.spot_asset > 0:
                    account.margin_position = round(account.margin_balance/user.spot_asset, 3)
                account.save()
        except Exception as error:
            send_notification("{} 资产同步异常: {}".format(user.nickname, str(error)))

def send_notification(text):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=8c58b08ee48b119709b064fd5bebb80b8ada055513d228b1102539716f8968e0'

    if text:
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
            requests.post(url, json=data, headers=headers)
