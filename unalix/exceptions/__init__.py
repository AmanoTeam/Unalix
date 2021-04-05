from .http import (
    UnsupportedProtocolError,
    ConnectError,
    TooManyRedirectsError
)

__all__ = [
    "UnsupportedProtocolError",
    "ConnectError",
    "TooManyRedirectsError"
]

__locals = locals()

for __name in __all__:
    setattr(__locals[__name], "__module__", "unalix.exceptions")
