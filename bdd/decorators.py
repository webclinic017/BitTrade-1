from django.core.exceptions import PermissionDenied
from bdd import settings

def admin_token(function):
    def wrap(request, *args, **kwargs):
        if settings.SECRET_KEY == request.GET.get('token'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
