from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
from .models import UserProfile, Following

class UserProfileAdmin(BaseUserAdmin):
    list_display = ('exchange', 'coin_list', 'is_staff', 'username', 'nickname', 'inviter', 'usdt_asset', 'spot_asset', 'usdt_unit', 'level', 'sync_time', 'date_joined')
    list_display_links = ('username', 'nickname')
    fields = ['exchange', 'coins', 'usdt_unit', 'is_staff', 'username', 'nickname', 'mobile', 'password', 'level', 'api_key', 'secret_key', 'passphrase', 'member_expire', 'date_joined']
    list_editable = ('exchange', 'is_staff', 'usdt_unit')
    search_fields = ('mobile', 'username', 'nickname')
    ordering = ('-level', '-usdt_unit', '-spot_asset', '-date_joined')
    fieldsets = None
    def coin_list(self, obj):
        return "\n".join([s.spot_symbol for s in obj.coins.all()])
    coin_list.short_description = '币种列表'

class FollowingAdmin(admin.ModelAdmin):
    list_display = ('user', 'coin', 'add_time')

admin.site.register(Following, FollowingAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
