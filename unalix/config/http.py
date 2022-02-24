import http

from .. import __version__


HTTP_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Connection": "close",
    "User-Agent": f"{__version__.__title__}/{__version__.__version__} (+{__version__.__homepage__})"
}

HTTP_METHOD = "GET"

HTTP_TIMEOUT = 3

HTTP_MAX_REDIRECTS = 13

HTTP_MAX_FETCH_SIZE = 5120

HTTP_MAX_RETRIES = 0

HTTP_STATUS_RETRY = (
    http.HTTPStatus.TOO_MANY_REQUESTS,
    http.HTTPStatus.INTERNAL_SERVER_ERROR,
    http.HTTPStatus.BAD_GATEWAY,
    http.HTTPStatus.SERVICE_UNAVAILABLE,
    http.HTTPStatus.GATEWAY_TIMEOUT
)

HTTP_STATUS_REDIRECT = (
    http.HTTPStatus.MOVED_PERMANENTLY,
    http.HTTPStatus.PERMANENT_REDIRECT,
    http.HTTPStatus.FOUND,
    http.HTTPStatus.SEE_OTHER,
    http.HTTPStatus.TEMPORARY_REDIRECT
)
