__all__ = ['REDIS']


from django.conf import settings

import random
import redis
import time


REDIS_POOL = redis.ConnectionPool(host=settings.APP_REDIS_HOST,
                                  port=settings.APP_REDIS_PORT,
                                  db=settings.APP_REDIS_DB)

REDIS = redis.Redis(connection_pool=REDIS_POOL)

def lock(key, timeout=60):
    key = 'lock_%s' % key
    value = random.randint(0, 100)
    result = REDIS.set(key, value, ex=timeout, nx=True)
    return result, value if result else None, timeout

def unlock(key, value):
    key = 'lock_%s' % key
    orig_value = REDIS.get(key)
    if orig_value == value:
        REDIS.delete(key)
        return True
    else:
        return False