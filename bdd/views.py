import os
import uuid
import string
import pprint
from ipware import get_client_ip
import logging
from django.http import Http404
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django_user_agents.utils import get_user_agent
from quant.models import Ohlcv, Coin, Signal
from bdd import settings
from users.models import UserProfile, SmsCaptcha

def index(request):
    return render(request, 'bdd/index.html')
