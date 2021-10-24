from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path('logout_site/', views.logout_site, name='logout'),
]
