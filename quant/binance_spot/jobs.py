import urllib, sys
import os
from django.utils import timezone
from celery.utils.log import get_task_logger
from celery import shared_task
import json
import requests
from datetime import datetime
from quant.models import Ohlcv, Coin
from users.models import UserProfile
from bdd import settings

from binance.client import Client as BinanceClient

logger = get_task_logger(__name__)
connect_timeout, read_timeout = 5.0, 30.0

@shared_task(bind=True, max_retries=1, expires=60)
def request_ohlcv(self, symbol, period, interval, size=200):
    binance_client = BinanceClient()
    result = binance_client.get_klines(symbol=symbol, interval=interval, limit=size)
    ohlcv, created = Ohlcv.objects.get_or_create(exchange='binance', symbol=symbol, period=period)
    ohlcv.update_time=timezone.now()
    ohlcv.data=json.dumps(result)
    ohlcv.save()

@shared_task(bind=True, max_retries=1, expires=60)
def sync_binance_assets(self):
    levels = {3: 1, 13: 2, 23: 3, 33: 4, 43: 5, 53: 6}
    minute = datetime.now().minute
    coin_list = list(Coin.objects.filter(open_trade=True).values_list('name', flat=True))
    if minute in list(levels.keys()):
        users = UserProfile.objects.filter(exchange__in=['binance_etf', 'binance'])
        for user in users:
            try:
                binance_client = BinanceClient(user.api_key, user.secret_key)
                usdt_balance = binance_client.get_asset_balance('USDT')
                if usdt_balance:
                    account, created = user.account_set.get_or_create(symbol='USDT')
                    if usdt_balance['locked']:
                        account.margin_frozen = round(float(usdt_balance['locked']), 4)
                    if usdt_balance['free']:
                        account.margin_available = round(float(usdt_balance['free']), 4)
                        account.margin_balance = round(float(usdt_balance['free']), 4)
                    if user.spot_asset and user.spot_asset > 0:
                        account.margin_position = round(account.margin_balance/user.spot_asset, 3)
                    account.save()
                    user.usdt_asset = account.margin_available
                else:
                    user.usdt_asset = 0
                total = user.usdt_asset
                accounts = user.account_set.filter(symbol__in=coin_list, margin_balance__gt=0).distinct()
                for account in accounts:
                    total = total + account.margin_balance
                #accounts_sum = user.account_set.filter(symbol__in=coin_list).aggregate(Sum('margin_balance'))
                user.spot_asset = round(total, 2)
                user.sync_time = datetime.now()
                user.save()

            except Exception as error:
                send_notification("{} 统计资产异常: {}".format(user.nickname, str(error)))

def send_notification(text):
    url = settings.DingDingUrl

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
