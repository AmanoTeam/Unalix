import http

from ..__version__ import __version__
from .. import types


HTTP_HEADERS = types.Dict({
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Connection": "close",
    "User-Agent": f"Unalix/{__version__} (+https://github.com/AmanoTeam/Unalix)"
})

HTTP_TIMEOUT = types.Int(8)

HTTP_MAX_REDIRECTS = types.Int(13)

HTTP_MAX_FETCH_SIZE = types.Int(1024 * 1024)

HTTP_MAX_RETRIES = types.Int(3)

HTTP_STATUS_RETRY = types.Tuple((
    http.HTTPStatus.TOO_MANY_REQUESTS,
    http.HTTPStatus.INTERNAL_SERVER_ERROR,
    http.HTTPStatus.BAD_GATEWAY,
    http.HTTPStatus.SERVICE_UNAVAILABLE,
    http.HTTPStatus.GATEWAY_TIMEOUT
))