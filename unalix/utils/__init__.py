from .http import (
    requote_uri,
    get_encoding_from_headers,
    filter_query
)

__all__ = [
    "requote_uri",
    "get_encoding_from_headers",
    "filter_query"
]

__locals = locals()

for __name in __all__:
    setattr(__locals[__name], "__module__", "unalix.utils")
