# vim: ts=4:sw=4:sts=4:et
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import
from django.shortcuts import render, Http404, HttpResponse, redirect
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

from django.core.cache import cache

import json
import functools


def login_required(method):

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        user_id = request.session.get("user_id")
        # check forward
        return method(*args, **kwargs)

    return wrapper

