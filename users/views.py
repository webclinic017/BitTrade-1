from datetime import datetime, timedelta
import requests

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, HttpResponse, HttpResponseRedirect, redirect
from django.db.models import Sum, Q
from django.contrib.auth import authenticate, logout
from django.contrib import auth
from django.contrib.auth import login as auth_login
from django_user_agents.utils import get_user_agent
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from ipware import get_client_ip

from .models import UserProfile



def logout_site(request):
    logout(request)
    return HttpResponseRedirect('/strategies/okex_bb')
