from .paths import (
    PATH_PACKAGE_DATA,
    PATH_RULESETS,
    PATH_COOKIES_ALLOW,
    PATH_BODY_REDIRECTS,
    PATH_CA_BUNDLE
)
from .http import (
    HTTP_HEADERS,
    HTTP_TIMEOUT,
    HTTP_MAX_REDIRECTS,
    HTTP_MAX_FETCH_SIZE,
    HTTP_STATUS_RETRY,
    HTTP_MAX_RETRIES
)

__all__ = [
    "PATH_PACKAGE_DATA",
    "PATH_RULESETS",
    "PATH_COOKIES_ALLOW",
    "PATH_BODY_REDIRECTS",
    "PATH_CA_BUNDLE",
    "HTTP_HEADERS",
    "HTTP_TIMEOUT",
    "HTTP_MAX_REDIRECTS",
    "HTTP_MAX_FETCH_SIZE",
    "HTTP_STATUS_RETRY",
    "HTTP_MAX_RETRIES"
]

__locals = locals()

for __name in __all__:
    setattr(__locals[__name], "__module__", "unalix.config")
