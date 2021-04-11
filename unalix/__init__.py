"""
    Unalix
    ~~~~~~~~

    Unalix is a small, dependency-free, fast Python package that implements
    the same regex rule processing mechanism used by the ClearURLs addon.

    Usage:

    Removing tracking fields

        >>> from unalix import clear_url
        >>> 
        >>> url = "https://deezer.com/track/891177062?utm_source=deezer"
        >>> 
        >>> clear_url(url)
        'https://deezer.com/track/891177062'

    Unshortening URLs

        >>> from unalix import unshort_url
        >>> 
        >>> url = "https://bitly.is/Pricing-Pop-Up"
        >>> 
        >>> unshort_url(url)
        'https://bitly.com/pages/pricing'

    Bugs:

    If something goes wrong, please open a issue at GitHub.
"""
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
    TooManyRedirectsError,
    MaxRetriesError
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
    "MaxRetriesError",
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

