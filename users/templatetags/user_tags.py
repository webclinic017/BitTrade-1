from django import template
from bdd import settings

register = template.Library()

@register.filter
def oss_image_url(value):
    return settings.OssPrivateBucket.sign_url('GET', value, 600000)


@register.filter
def invite_url(value):
    print(value)
    return settings.SiteUrl + '/i/' + value
