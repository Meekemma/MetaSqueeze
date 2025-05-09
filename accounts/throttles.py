# accounts/throttles.py

import logging
from rest_framework.throttling import ScopedRateThrottle, SimpleRateThrottle
from rest_framework.exceptions import Throttled
 

logger = logging.getLogger(__name__)

class BaseScopedThrottle(ScopedRateThrottle):
    """
    A base class for scoped throttles that logs debug information.
    """

    def allow_request(self, request, view):
        cache_key = self.get_cache_key(request, view)
        throttle_name = (self.scope or self.__class__.__name__)
        logger.debug(f"{throttle_name}Throttle: cache_key={cache_key}")
        try:
            allowed = super().allow_request(request, view)
            cache_value = self.cache.get(cache_key)
            logger.debug(f"{throttle_name}Throttle: allowed={allowed}, cache_value={cache_value}")
            return allowed
        except Exception as e:
            logger.error(f"{throttle_name}Throttle error: {str(e)}")
            raise


class RegisterThrottle(BaseScopedThrottle):
    scope = 'register'



class LoginThrottle(BaseScopedThrottle):
    scope = 'login'

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not allowed:
            from rest_framework.exceptions import Throttled
            raise Throttled(detail="Too many login attempts. Please wait a minute.")
        return allowed




class LogoutThrottle(BaseScopedThrottle):
    scope = 'logout'

class IPThrottle(SimpleRateThrottle):
    scope = 'ip'

    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        cache_key = self.cache_format % {'scope': self.scope, 'ident': ip}
        logger.debug(f"IPThrottle: ip={ip}, cache_key={cache_key}")
        return cache_key
