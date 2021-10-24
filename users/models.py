import hashlib

from datetime import datetime
from urllib.parse import quote
from django.utils.http import urlencode
from django.db import models
from django.db.models import Avg, Count, Min, Sum
from django.contrib.auth.models import AbstractUser, User
from django_countries.fields import CountryField
from random import randint

from bdd import settings
from quant.models import Coin, Order, Strategy

class UserProfile(AbstractUser):
    """
    用户模块，继承Django默认的User，添加新字段
    """
    # null=True 数据库可空 blank=True HTML可空
    client_ip = models.CharField(max_length=30, null=True, blank=True, verbose_name="IP地址")
    coins = models.ManyToManyField(Coin, blank=True)
    strategies = models.ManyToManyField(Strategy, blank=True)
    api_permissions = models.CharField(max_length=200, null=True, blank=True, verbose_name="接口权限")
    spot_strategy = models.CharField(max_length=30, null=True, blank=True, choices=list(map(lambda x: (x, x), settings.ActiveStrategies.keys())), verbose_name="现货策略")
    api_key = models.CharField(max_length=200, null=True, blank=True, verbose_name="API KEY")
    secret_key = models.CharField(max_length=200, null=True, blank=True, verbose_name="Secret KEY")
    passphrase = models.CharField(max_length=200, null=True, blank=True, verbose_name="Passphrase")
    inviter = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='invitees')
    nickname = models.CharField(null=True, verbose_name='昵称', max_length=30)
    invitation_code = models.CharField(null=True, verbose_name='邀请码', max_length=30)
    mobile = models.CharField(max_length=20, null=True, blank=True, verbose_name="手机号码")
    openid = models.CharField(null=True, verbose_name='openid', max_length=30)
    avatar = models.CharField(null=True, verbose_name='头像', max_length=200)
    level = models.IntegerField(default=0, verbose_name="会员等级")
    member_expire = models.DateTimeField(null=True, blank=True, verbose_name="会员到期时间")
    total_points = models.IntegerField(default=0, verbose_name="累计积分")
    remain_points = models.IntegerField(default=0, verbose_name="剩余积分")
    exchange = models.CharField(null=True, blank=True, verbose_name='交易所', choices=[('binance', '币安现货'), ('binance_futures', '币安期货'), ('okex_spot', 'okex现货')], max_length=200)
    is_kol = models.BooleanField(default=False, verbose_name="是否KOL")
    is_vip = models.BooleanField(default=False, verbose_name="是否VIP")
    usdt_unit = models.FloatField(default=0, verbose_name="现货资金分配")
    swap_unit = models.FloatField(default=0, verbose_name="永续资金分配")
    usdt_asset = models.FloatField(default=0, verbose_name="USDT资产")
    spot_asset = models.FloatField(default=0, verbose_name="总资产估值")
    sync_time = models.DateTimeField(null=True, blank=True, verbose_name="资产同步时间")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def referral_count(self):
        return self.invitees.count()

    def member_level(self):
        return self.level

    def token(self):
        t, created = Token.objects.get_or_create(user=self)
        return 'Token ' + t.key

    def jpush_alias(self):
        md5 = hashlib.md5(self.token().encode())
        return md5.hexdigest()


    def __str__(self):
        return self.nickname or self.username

class Following(models.Model):
    user = models.ForeignKey(UserProfile, null=True, on_delete=models.CASCADE, related_name='user_followings')
    coin = models.ForeignKey(Coin, null=True, on_delete=models.CASCADE, related_name='coin_followings')
    period = models.CharField(max_length=30, default='m', verbose_name="周期")
    deduct_time = models.DateTimeField(default=datetime.now, verbose_name="扣除积分时间")
    normal = models.BooleanField(default=True, verbose_name="状态")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "订阅"
        verbose_name_plural = verbose_name


    def __str__(self):
        return self.coin.symbol



class SmsCaptcha(models.Model):
    """
    短信验证码
    """
    dial_code = models.CharField(default='86', verbose_name='国家手机代码', max_length=10)
    mobile = models.CharField(max_length=20, verbose_name="手机号码", null=True, blank=True)
    result = models.CharField(max_length=10, verbose_name="发送结果")
    token = models.CharField(max_length=10, verbose_name="验证码")
    scene = models.CharField(max_length=10, verbose_name="场景", null=True, blank=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
