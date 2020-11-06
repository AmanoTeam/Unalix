from http.client import HTTPResponse, HTTPConnection, HTTPSConnection
import os
from ._exceptions import InvalidScheme, InvalidContentEncoding
import ssl
from urllib.parse import urlparse, urlunparse, ParseResult
import zlib

from ._config import (
    cafile,
    capath,
    python_version,
    ssl_ciphers,
    ssl_options,
    ssl_verify_flags,
    timeout
)
from ._types import Connection

# https://github.com/encode/httpx/blob/0.16.1/httpx/_decoders.py#L36
def decode_from_deflate(content: bytes) -> bytes:
    """This function is used to decode deflate responses."""
    try:
        return zlib.decompressobj.decompress(content)
    except zlib.error:
        return zlib.decompressobj(-zlib.MAX_WBITS).decompress(content)

# https://github.com/encode/httpx/blob/0.16.1/httpx/_decoders.py#L65
def decode_from_gzip(content: bytes) -> bytes:
    """This function is used to decode gzip responses."""
    return zlib.decompressobj(zlib.MAX_WBITS|16).decompress(content)

# https://github.com/encode/httpx/blob/0.16.1/httpx/_config.py#L98
# https://github.com/encode/httpx/blob/0.16.1/httpx/_config.py#L151
def create_ssl_context() -> ssl.SSLContext:
    """This function creates the default SSL context for HTTPS connections.

    Usage:
      >>> from unalix._http import create_ssl_context
      >>> create_ssl_context()
      <ssl.SSLContext object at 0xad6a9070>
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.options = ssl_options
    context.verify_flags = ssl_verify_flags
    context.set_ciphers(ssl_ciphers)

    if ssl.HAS_ALPN:
        context.set_alpn_protocols(["http/1.1"])

    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.load_verify_locations(cafile=cafile, capath=capath)

    if python_version >= 3.7:
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3

    # Signal to server support for PHA in TLS 1.3. Raises an
    if python_version >= 3.8:
        context.post_handshake_auth = True

    # Disable using 'commonName' for SSLContext.check_hostname
    # when the 'subjectAltName' extension isn't available.
    if python_version >= 3.7:
        context.hostname_checks_common_name = False

    return context

def create_connection(scheme: str, netloc: str) -> Connection: # type: ignore
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

def handle_redirects(url: ParseResult, response: HTTPResponse) -> ParseResult:
    """This function is used to handle HTTP redirects. It parses the value of the "Location" header."""
    location = response.headers.get("Location")

    if location is None:
        return None

    # https://stackoverflow.com/a/27357138
    location = location.encode("latin1").decode()

    if location.startswith("http://") or location.startswith("https://"):
        return urlparse(location)

    scheme, netloc, path, params, query, fragment = url

    if location.startswith("/"):
        redirect_url = urlunparse((scheme, netloc, location, "", "", ""))
        return urlparse(redirect_url)

    path = os.path.join(os.path.dirname(path), location)
    redirect_url = urlunparse((scheme, netloc, path, "", "", ""))

    return urlparse(redirect_url)

def get_encoded_content(response: HTTPResponse) -> str:
    """This function is used to decode gzip and deflate responses. It also parses unencoded/plain text responses."""
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
        raise InvalidContentEncoding(f"Expected 'identity', 'gzip' or 'deflate', but got: {content_encoding}")

    return content_as_bytes.decode()

def add_missing_attributes(url: ParseResult, headers: dict, connection: Connection) -> None:

    def add_unredirected_header(key: str, val: str) -> None:
        connection.headers.update({key: val}) # type: ignore

    connection.has_header = lambda header_name: False # type: ignore
    connection.add_unredirected_header = add_unredirected_header # type: ignore
    connection.get_full_url = lambda: urlunparse(url) # type: ignore

    connection.unverifiable = True  # type: ignore
    connection.headers = headers # type: ignore
    connection.origin_req_host = url.netloc # type: ignore

context = create_ssl_context()