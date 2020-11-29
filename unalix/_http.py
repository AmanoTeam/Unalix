from http.client import HTTPConnection, HTTPSConnection
from http.cookiejar import CookieJar, DefaultCookiePolicy
import os
import ssl
from urllib.parse import urlparse, urlunparse
import zlib

from ._config import (
    allowed_cookies,
    data,
    python_version,
    timeout
)
from ._exceptions import InvalidScheme, InvalidContentEncoding
from ._utils import requote_uri

# https://github.com/encode/httpx/blob/0.16.1/httpx/_decoders.py#L36
def decode_from_deflate(content):
    """This function is used to decode deflate responses."""
    try:
        return zlib.decompressobj.decompress(content)
    except zlib.error:
        return zlib.decompressobj(-zlib.MAX_WBITS).decompress(content)


# https://github.com/encode/httpx/blob/0.16.1/httpx/_decoders.py#L65
def decode_from_gzip(content):
    """This function is used to decode gzip responses."""
    return zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(content)


# https://github.com/encode/httpx/blob/0.16.1/httpx/_config.py#L98
# https://github.com/encode/httpx/blob/0.16.1/httpx/_config.py#L151
def create_ssl_context():
    """This function creates the default SSL context for HTTPS connections.

    Usage:
      >>> from unalix._http import create_ssl_context
      >>> create_ssl_context()
      <ssl.SSLContext object at 0xad6a9070>
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)

    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True

    # Ciphers list for HTTPS connections
    ssl_ciphers = ":".join([
        "ECDHE+AESGCM",
        "ECDHE+CHACHA20",
        "DHE+AESGCM",
        "DHE+CHACHA20",
        "ECDH+AESGCM",
        "DH+AESGCM",
        "ECDH+AES",
        "DH+AES",
        "RSA+AESGCM",
        "RSA+AES",
        "!aNULL",
        "!eNULL",
        "!MD5",
        "!DSS"
    ])

    context.set_ciphers(ssl_ciphers)

    # Default options for SSL contexts
    ssl_options = (
        ssl.OP_ALL
        | ssl.OP_NO_COMPRESSION
        | ssl.OP_SINGLE_DH_USE
        | ssl.OP_SINGLE_ECDH_USE
    )
    
    # These options are deprecated since Python 3.7
    if python_version == 3.6:
        ssl_options |= (
            ssl.OP_NO_SSLv2
            | ssl.OP_NO_SSLv3
            | ssl.OP_NO_TLSv1
            | ssl.OP_NO_TLSv1_1
            | ssl.OP_NO_TICKET
        )

    context.options = ssl_options

    # Default verify flags for SSL contexts
    ssl_verify_flags = (
        ssl.VERIFY_X509_STRICT
        | ssl.VERIFY_X509_TRUSTED_FIRST
        | ssl.VERIFY_DEFAULT
    )

    context.verify_flags = ssl_verify_flags

    # CA bundle for server certificate validation
    cafile = f"{data}/ca-bundle.crt"
    
    # CA certs path for server certificate validation
    capath = os.path.dirname(cafile)

    context.load_verify_locations(cafile=cafile, capath=capath)

    if ssl.HAS_ALPN:
        context.set_alpn_protocols(["http/1.1"])

    if python_version >= 3.7:
        # Only available in Python 3.7 or higher
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3

        # Disable using 'commonName' for SSLContext.check_hostname
        # when the 'subjectAltName' extension isn't available.
        context.hostname_checks_common_name = False

        # ssl.OP_NO_RENEGOTIATION is not available on Python versions bellow 3.7
        ssl_options |= ssl.OP_NO_RENEGOTIATION

    if python_version >= 3.8:
        # Signal to server support for PHA in TLS 1.3.
        context.post_handshake_auth = True

    return context


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
        connection = HTTPConnection(netloc, timeout=timeout)
    elif scheme == "https":
        connection = HTTPSConnection(netloc, context=context, timeout=timeout)
    else:
        raise InvalidScheme(f"Expecting 'http' or 'https', but got: {scheme}")

    return connection


def handle_redirects(url, response):
    """This function is used to handle HTTP redirects."""
    location = response.headers.get("Location")

    if location is None:
        return None

    # https://stackoverflow.com/a/27357138
    location = requote_uri(location.encode("latin1").decode('utf-8'))

    if location.startswith("http://") or location.startswith("https://"):
        return location

    scheme, netloc, path, params, query, fragment = urlparse(url)

    if location.startswith("/"):
        return urlunparse((scheme, netloc, location, "", "", ""))

    path = os.path.join(os.path.dirname(path), location)

    return urlunparse((scheme, netloc, path, "", "", ""))


def get_encoded_content(response):
    """This function is used to decode gzip and deflate responses."""
    content_encoding = response.headers.get("Content-Encoding")

    if content_encoding is None:
        content_encoding = "identity"

    if content_encoding == "identity":
        content_as_bytes = response.read()
    elif content_encoding == "gzip":
        content_as_bytes = decode_from_gzip(response.read())
    elif content_encoding == "deflate":
        content_as_bytes = decode_from_deflate(response.read())
    else:
        raise InvalidContentEncoding(
            f"Expected 'identity', 'gzip' or 'deflate', but got: {content_encoding}"
        )

    return content_as_bytes.decode(errors="ignore")


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

    cookie, policy = CookieJar(), DefaultCookiePolicy()

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


context = create_ssl_context()