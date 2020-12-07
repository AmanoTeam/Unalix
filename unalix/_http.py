from http.client import HTTPConnection, HTTPSConnection
from http.cookiejar import CookieJar, DefaultCookiePolicy
import os
from urllib.parse import urlparse, urlunparse

from ._config import (
    allowed_cookies,
    httpopt
)
from ._exceptions import InvalidScheme
from ._utils import requote_uri

def create_connection(scheme, netloc):
    """This function is used to create HTTP and HTTPS connections.

    Parameters:
        scheme (`str`):
            Scheme (must be 'http' or 'https').

        netloc (`str`):
            Netloc or hostname.

    Raises:
        InvalidScheme: In case the provided *scheme* is not valid.

    Usage:
      >>> from unalix._utils import create_connection
      >>> create_connection("http", "example.com")
      <http.client.HTTPConnection object at 0xad219bb0>
    """
    if scheme == "http":
        connection = HTTPConnection(netloc, timeout=httpopt.timeout)
    elif scheme == "https":
        connection = HTTPSConnection(netloc, context=httpopt.ssl_context, timeout=httpopt.timeout)
    else:
        raise InvalidScheme(f"Expecting 'http' or 'https', but got: {scheme}")

    return connection


def handle_redirects(url, response):
    """This function is used to handle HTTP redirects."""
    location = response.headers.get("Location")

    if location is None:
        content_location = response.headers.get("Content-Location")
        if content_location is None:
            return None
        else:
            location = content_location

    # https://stackoverflow.com/a/27357138
    location = requote_uri(
        location.encode(encoding="latin1").decode(encoding='utf-8')
    )

    if location.startswith("http://") or location.startswith("https://"):
        return location

    scheme, netloc, path, params, query, fragment = urlparse(url)

    if location.startswith("/"):
        return urlunparse(
            (scheme, netloc, location, "", "", "")
        )

    path = os.path.join(os.path.dirname(path), location)

    return urlunparse(
        (scheme, netloc, path, "", "", "")
    )


def add_missing_attributes(url, connection):

    try:
        connection.cookies
    except AttributeError:
        connection.cookies = {}

    def add_unredirected_header(key, value):
        connection.headers.update(
            {
                key: value
            }
        )

    connection.has_header = lambda header_name: False
    connection.add_unredirected_header = add_unredirected_header
    connection.get_full_url = lambda: url

    connection.unverifiable = True
    connection.headers = {}
    connection.origin_req_host = urlparse(url).netloc


def create_cookie_jar(policy_type=None):

    cookie, policy = (
        CookieJar(), DefaultCookiePolicy()
    )

    if policy_type == "reject_all":
        policy.set_ok = lambda cookie, request: False
    elif policy_type == "allow_all":
        policy.set_ok = lambda cookie, request: True
    elif policy_type == "allow_if_needed":
        policy.set_ok = lambda cookie, request: (
            cookie.domain in allowed_cookies
        )

    cookie.set_policy(policy)

    return cookie

