# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import django
import socket
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bdd.settings')
django.setup()

from django.conf import settings

from celery import Celery
from celery.schedules import crontab
from celery import shared_task
from celery.utils.log import get_task_logger

from quant.binance_spot.jobs import request_ohlcv as request_binance_spot_ohlcv
from quant.binance_spot.trade_bot import trade_task as binance_spot_trade_task
from quant.binance_spot.jobs import sync_binance_assets as sync_binance_spot_assets

from bdd.config.binance_spot_coins import BinanceSpotCoins
# set the default Django settings module for the 'celery' program.

logger = get_task_logger(__name__)

app = Celery('bdd')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    if socket.gethostname() == 'spot1':
        pass

        for key, value in BinanceSpotCoins.items():
            name = key
            spot_symbol = value['spot_symbol']
            sender.add_periodic_task(30, request_binance_spot_ohlcv.s(spot_symbol, '15min', '15m'))
            sender.add_periodic_task(value['time'], binance_spot_trade_task.s(name, spot_symbol))
        sender.add_periodic_task(60, sync_binance_spot_assets.s())
