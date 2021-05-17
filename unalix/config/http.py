import http

from ..__version__ import __version__


HTTP_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Connection": "close",
    "User-Agent": f"Unalix/{__version__} (+https://github.com/AmanoTeam/Unalix)"
}

HTTP_METHOD = "GET"

HTTP_TIMEOUT = 8

HTTP_MAX_REDIRECTS = 13

HTTP_MAX_FETCH_SIZE = 1024 * 1024

HTTP_MAX_RETRIES = 0

HTTP_STATUS_RETRY = (
    http.HTTPStatus.TOO_MANY_REQUESTS,
    http.HTTPStatus.INTERNAL_SERVER_ERROR,
    http.HTTPStatus.BAD_GATEWAY,
    http.HTTPStatus.SERVICE_UNAVAILABLE,
    http.HTTPStatus.GATEWAY_TIMEOUT
)

HTTP_STATUS_REDIRECT = (
    HTTPStatus.MOVED_PERMANENTLY,
    HTTPStatus.PERMANENT_REDIRECT,
    HTTPStatus.FOUND,
    HTTPStatus.SEE_OTHER,
    HTTPStatus.TEMPORARY_REDIRECT
)
