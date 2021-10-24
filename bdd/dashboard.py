"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'xdis.dashboard.CustomIndexDashboard'
"""
import datetime

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name

from django.db.models import Count, Min, Sum, Avg

from users.models import UserProfile, SmsCaptcha, Certification

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Administration'),
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('AppList: Applications'),
            collapsible=True,
            column=1,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*',),
        ))

        users_count = UserProfile.objects.aggregate(Count('id')).get('id__count')
        today_users_count = UserProfile.objects.filter(date_joined__startswith=datetime.date.today()).aggregate(Count('id')).get('id__count')
        # append another link list module for "support".
        self.children.append(modules.LinkList(
            '数据统计',
            column=2,
            children=[
                {
                    'title': '总用户数: ' + str(users_count),
                    'url': 'users',
                    'external': False,
                },
                {
                    'title': '今日用户数: ' + str(today_users_count),
                    'url': 'users',
                    'external': False,
                },
            ]
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))
