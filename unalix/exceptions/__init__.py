from .http import (
    UnsupportedProtocolError,
    ConnectError,
    TooManyRedirectsError,
    MaxRetriesError
)

__all__ = [
    "UnsupportedProtocolError",
    "ConnectError",
    "TooManyRedirectsError",
    "MaxRetriesError"
]

__locals = locals()

for __name in __all__:
    setattr(__locals[__name], "__module__", "unalix.exceptions")
