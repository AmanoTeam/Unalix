import http.cookiejar

from .. import config
from . import coreutils


# Custom policies for cookies

ALLOWED_DOMAINS = coreutils.domains_from_files(config.PATH_COOKIES_ALLOW)

# reject all cookies
COOKIE_REJECT_ALL = http.cookiejar.DefaultCookiePolicy()
COOKIE_REJECT_ALL.set_ok = lambda cookie, request: False

# allow all cookies
COOKIE_ALLOW_ALL = http.cookiejar.DefaultCookiePolicy()
COOKIE_ALLOW_ALL.set_ok = lambda cookie, request: True

# only allow cookies for domains that are known to not work without them
COOKIE_STRICT_ALLOW = http.cookiejar.DefaultCookiePolicy()
COOKIE_STRICT_ALLOW.set_ok = lambda cookie, request: (
    True if cookie.domain in ALLOWED_DOMAINS else False
)
