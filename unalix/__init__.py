from .core.url_cleaner import clear_url
from .core.url_unshort import unshort_url
from .core.cookie_policies import (
    COOKIE_REJECT_ALL,
    COOKIE_ALLOW_ALL,
    COOKIE_STRICT_ALLOW
)
from .core.ssl_context import SSL_CONTEXT_VERIFIED, SSL_CONTEXT_UNVERIFIED
from .__version__ import __description__, __title__, __version__
from .exceptions import (
    UnsupportedProtocolError,
    ConnectError,
    TooManyRedirectsError
)


__all__ = [
    "__description__",
    "__title__",
    "__version__",
    "clear_url",
    "unshort_url",
    "UnsupportedProtocolError",
    "ConnectError",
    "TooManyRedirectsError",
    "COOKIE_REJECT_ALL",
    "COOKIE_ALLOW_ALL",
    "COOKIE_STRICT_ALLOW",
    "SSL_CONTEXT_VERIFIED",
    "SSL_CONTEXT_UNVERIFIED"
]

__locals = locals()

for __name in __all__:
    if not __name.startswith("__"):
        try:
            setattr(__locals[__name], "__module__", "unalix")
        except AttributeError:
            pass

