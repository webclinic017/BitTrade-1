import json
from django.contrib import admin
from quant.models import *

class OhlcvAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'symbol', 'period', 'data_length', 'update_time')
    list_display_links = ('symbol',)
    search_fields = ('exchange', 'symbol', 'period')
    ordering = ('-update_time',)
    def data_length(self, obj):
        if obj.data:
            return len(json.loads(obj.data))

    data_length.short_description = '数据集'

admin.site.register(Ohlcv, OhlcvAdmin)

class CoinAdmin(admin.ModelAdmin):
    list_display  = ('open_trade', 'exchange', 'name', 'spot_symbol', 'position', 'strategy', 'spot_symbol', 'spot_price', 'start_position', 'profit_price', 'ma_size', 'qty_size', 'update_time')
    list_display_links = ('name', 'spot_symbol')
    list_editable = ('open_trade', 'strategy', 'ma_size', 'start_position', 'profit_price', 'qty_size')
    fields  = ['open_trade', 'name', 'logo', 'exchange', 'spot_symbol', 'position', 'status']
    search_fields = ('name', 'spot_symbol')
    ordering = ('-open_trade', 'exchange', 'strategy', 'name')

admin.site.register(Coin, CoinAdmin)

class SignalAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'coin', 'symbol', 'action', 'direction', 'price', 'last_price', 'profit', 'leverage', 'add_time', 'update_time')
    list_display_links = ('symbol', 'coin')
    fields  = ['strategy', 'symbol', 'price', 'last_price', 'profit', 'leverage', 'add_time']
    search_fields = ('symbol', 'strategy')
    ordering = ('-update_time',)

admin.site.register(Signal, SignalAdmin)


class StrategyAdmin(admin.ModelAdmin):
    list_display = ('status', 'name', 'code', 'state', 'period', 'taget_profit', 'risk', 'ip', 'tags', 'max_users', 'start_time', 'add_time')
    list_display_links = ('name', 'code')
    list_editable = ('period', 'risk', 'tags')
    search_fields = ('name', 'code', 'hostname')
    ordering = ('name',)

admin.site.register(Strategy, StrategyAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'trade_id', 'symbol', 'direction', 'price', 'volume', 'total', 'commission', 'created_at', 'add_time')
    ordering = ('-created_at', 'trade_id')
    search_fields = ('user__username', 'user__nickname', 'trade_id', 'symbol')
admin.site.register(Order, OrderAdmin)
