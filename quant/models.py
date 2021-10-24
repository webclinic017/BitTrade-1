import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta, date
from django.db.models import Avg, Count, Min, Sum
from django.db import models
from django.contrib.postgres.fields import HStoreField, JSONField
from django.conf import settings
from bdd.settings import ActiveStrategies
from django.apps import apps

class Strategy(models.Model):
    name = models.CharField(null=True, max_length=30, verbose_name="名称")
    code = models.CharField(max_length=30, null=True, db_index=True, choices=list(map(lambda x: (x, x), ActiveStrategies.keys())), verbose_name="策略代码")
    period = models.CharField(default='15min', max_length=30, choices=[['5min', '5min'], ['15min', '15min']], verbose_name="交易周期")
    ip = models.CharField(max_length=100, blank=True, null=True, verbose_name="服务器IP")
    risk = models.CharField(max_length=100, blank=True, null=True, verbose_name="风险等级")
    tags = models.CharField(null=True, max_length=100, verbose_name="Tag")
    max_users = models.IntegerField(default=0, verbose_name="最大参与人数")
    status = models.BooleanField(default=False, verbose_name="是否开启")
    state = models.IntegerField(default=0, choices=[[0, '未开启'], [1, '进行中'], [2, '已满员']], verbose_name="状态")
    taget_profit = models.FloatField(default=0, verbose_name="预期月化")
    start_time = models.DateTimeField(null=True, verbose_name="开始时间")
    push_url = models.TextField(blank=True, null=True, verbose_name="推送链接")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def total_profit(self):
        return 0.8

    def users_count(self):
        users_count = apps.get_model('users', 'UserProfile').objects.exclude(api_key__isnull=True).exclude(secret_key__isnull=True).filter(strategies__code=self.code).count()
        return users_count

    def __str__(self):
        return self.code


class Coin(models.Model):

    trend = models.FloatField(null=True, default=1, verbose_name="趋势")

    strategy = models.ForeignKey(Strategy, models.SET_NULL, blank=True, null=True)

    name = models.CharField(null=True, max_length=30, verbose_name="名称")
    symbol = models.CharField(max_length=30, blank=True, null=True, verbose_name="期货交易对")
    spot_symbol = models.CharField(max_length=30, blank=True, null=True, verbose_name="现货交易对")
    exchange = models.CharField(null=True, max_length=30, db_index=True, verbose_name="交易所")

    status = models.IntegerField(default=0, verbose_name="状态")

    spot_price = models.FloatField(null=True, verbose_name="现货价格")
    swap_price = models.FloatField(null=True, verbose_name="期货价格")

    buy_price = models.FloatField(null=True, verbose_name="买五价格")
    sell_price = models.FloatField(null=True, verbose_name="卖五价格")

    period = models.CharField(default='15min', max_length=30, choices=[['5min', '5min'], ['15min', '15min'], ['4hour', '4hour']], verbose_name="交易周期")

    ma_size = models.IntegerField(default=48, verbose_name="MA SIZE")
    profit_price = models.FloatField(default=0, verbose_name="止盈价格")

    add_size = models.FloatField(default=0.01, verbose_name="补仓")

    qty_size = models.IntegerField(default=100, verbose_name="数量小数位")

    logo = models.CharField(null=True, blank=True, max_length=100, verbose_name="LOGO")

    open_trade = models.BooleanField(default=False, verbose_name="开通交易")


    position = models.IntegerField(default=0, blank=True, verbose_name="当前仓位")
    start_position = models.IntegerField(default=1, verbose_name="实盘仓位")

    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    target_profit = models.FloatField(null=True, default=0.1, verbose_name="预计月化")

    sync_time = models.DateTimeField(null=True, blank=True, verbose_name="订单同步时间")

    class Meta:
        unique_together = [["exchange", "symbol", "spot_symbol"]]

    def users_count(self):
        return self.userprofile_set.distinct().count()

    def __str__(self):
        if self.exchange and self.spot_symbol:
            return self.exchange + ' ' + self.name
        else:
            return self.name

class CoinPosition(models.Model):
    coin = models.ForeignKey(Coin, null=False, on_delete=models.CASCADE)
    price = models.FloatField(null=True, blank=True, max_length=30, verbose_name="价格")
    volume = models.FloatField(default=0, max_length=30, verbose_name="数量")
    position = models.IntegerField(null=True, blank=True, verbose_name="仓位")
    update_time = models.DateTimeField(default=datetime.now, verbose_name="更新时间")

    class Meta:
        unique_together = [["coin", "position"],]
        verbose_name = "仓位"
        verbose_name_plural = verbose_name


class Ohlcv(models.Model):
    exchange = models.CharField(null=True, max_length=30, db_index=True, verbose_name="交易所")
    symbol = models.CharField(db_index=True, max_length=30, verbose_name="交易对")
    period = models.CharField(db_index=True, max_length=30, verbose_name="周期")
    data = models.TextField(verbose_name="数据")
    update_time = models.DateTimeField(default=datetime.now, verbose_name="更新时间")

    def get_df(self):
        if self.exchange in ['okex_spot', 'okex_swap']:
            df = pd.read_json(self.data, orient='records')
            df.columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'currency_volume']
            df['time'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Asia/Shanghai')
            df = df.sort_values(by=['timestamp'], ascending=True)
            return df
        elif self.exchange in ['binance', 'binance_futures']:
            df = pd.read_json(self.data)
            df.columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_']
            df.drop('_', axis=1, inplace=True)
            df['time'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert('Asia/Shanghai')
            df = df.sort_values(by=['time'], ascending=True)
            #df.set_index('time', inplace=True)
            return df
        elif self.exchange in ['hb_spot']:
            df = pd.read_json(self.data)
            #df.columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_']
            df['time'] = pd.to_datetime(df['id'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai')
            df = df.sort_values(by=['time'], ascending=True)
            #df.set_index('time', inplace=True)
            return df

    class Meta:
        index_together = [
            ["exchange", "symbol", "period"],
        ]
        unique_together = [["exchange", "symbol", "period"],]


    def __str__(self):
        return str(self.symbol)

class Signal(models.Model):
    coin = models.ForeignKey(Coin, null=True, on_delete=models.CASCADE)
    leverage = models.IntegerField(null=False, default=0, verbose_name="杠杠")
    symbol = models.CharField(db_index=True, null=True, max_length=30, verbose_name="交易对")
    code = models.CharField(null=True, blank=True, max_length=100, verbose_name="代码")
    period = models.CharField(null=True, blank=True, max_length=30, verbose_name="周期")
    strategy = models.CharField(null=True, blank=True, max_length=30, verbose_name="策略")
    exchange = models.CharField(null=True, max_length=30, db_index=True, verbose_name="交易所")
    price = models.FloatField(null=True, blank=True, max_length=30, verbose_name="平均价格")
    best_price = models.FloatField(null=True, blank=True, max_length=30, verbose_name="委托价格")
    init_price = models.FloatField(null=True, default=0, max_length=30, verbose_name="开单价格")
    last_price = models.FloatField(null=True, default=0, max_length=30, verbose_name="加仓价格")
    profit = models.FloatField(null=True, blank=True, max_length=30, verbose_name="利润")
    action = models.CharField(null=True, max_length=100, choices=[('open', '开'), ('close', '平')], verbose_name="交易")
    direction = models.CharField(max_length=30, null=True, choices=[('long', '多'), ('short', '空')], verbose_name="方向")
    featured = models.BooleanField(default=False, verbose_name="案例信号")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=datetime.now, verbose_name="更新时间")
    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'period']),
            models.Index(fields=['symbol', 'strategy']),
        ]
        verbose_name = "信号"
        verbose_name_plural = verbose_name


    def __str__(self):
        return self.symbol

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        null=True,
        on_delete=models.CASCADE,
    )
    symbol = models.CharField(max_length=200, null=True, db_index=True, verbose_name="品种代码")
    trade_id = models.CharField(max_length=200, null=True, db_index=True, verbose_name="成交ID")
    volume = models.FloatField(null=True, blank=True, max_length=30, verbose_name="成交数量")
    commission = models.FloatField(default=0, blank=True, max_length=30, verbose_name="交易费")
    total = models.FloatField(null=True, blank=True, max_length=30, verbose_name="成交额")
    price = models.FloatField(null=True, blank=True, max_length=30, verbose_name="委托价格")
    direction = models.CharField(max_length=20, null=True, blank=True, verbose_name="买卖方向")
    created_at = models.DateTimeField(null=True, verbose_name="成交时间")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="同步时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def user_name(self):
        if self.user is not None:
            return self.user.nickname

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = verbose_name
    def __str__(self):
        return str(self.trade_id)
