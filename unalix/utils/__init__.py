from .http import requote_uri

__all__ = [
    "requote_uri"
]

__locals = locals()

for __name in __all__:
	setattr(__locals[__name], "__module__", "unalix.utils")
