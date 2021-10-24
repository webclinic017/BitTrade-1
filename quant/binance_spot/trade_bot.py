import os
import socket
import requests
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Sum

from users.models import UserProfile
from quant.models import Coin
from binance.client import Client as BinanceClient
from bdd.config.binance_spot_coins import BinanceSpotCoins

@shared_task(bind=True, max_retries=1, expires=60)
def trade_task(self, name, spot_symbol):

    coin, created = Coin.objects.get_or_create(exchange='binance', name=name, spot_symbol=spot_symbol)

    strategy = coin.strategy
    if strategy and coin.open_trade:
        binance_client = BinanceClient()
        order_book = binance_client.get_order_book(symbol=spot_symbol, limit=5)
        coin.buy_price = float(order_book['bids'][-1][0]) #买价(Bid)、卖价(Ask)
        coin.spot_price = float(order_book['bids'][0][0])
        coin.sell_price = float(order_book['asks'][-1][0])
        coin.save()
