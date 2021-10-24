"""xbank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, handler404, handler500
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from quant import coin_views
from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache

static_view = never_cache(serve)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('users/', include('users.urls')),
    path('coins/', coin_views.index),
    path('q/<str:exchange>/', include('quant.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
