from django.urls import path, include

from . import coin_views

app_name = 'quant'

urlpatterns = [
    path('coins/<int:coin_id>/minus', coin_views.minus),
    path('coins/<int:coin_id>/close', coin_views.close),
    path('coins/<int:coin_id>/add', coin_views.add),
]
