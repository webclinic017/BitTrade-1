# -*- coding:utf-8 -*-
import datetime

def get_object_or_none(models, *args, **kwargs):
    try:
        return models.objects.get(*args, **kwargs)
    except models.DoesNotExist:
        return None

def format_datetime(dt):
    return datetime.datetime.strftime(dt, "%Y%m%d%H%M")