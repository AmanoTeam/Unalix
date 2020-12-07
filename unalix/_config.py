import json
import os
import ssl

from ._utils import get_python_version
from .__version__ import __version__

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
    ssl_ciphers = ":".join(
        (
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
        )
    )

    context.set_ciphers(ssl_ciphers)

    # Default options for SSL contexts
    ssl_options = (
        ssl.OP_ALL
        | ssl.OP_NO_COMPRESSION
        | ssl.OP_SINGLE_DH_USE
        | ssl.OP_SINGLE_ECDH_USE
    )

    python_version = get_python_version()

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
        ssl.VERIFY_X509_TRUSTED_FIRST
        | ssl.VERIFY_DEFAULT
    )

    context.verify_flags = ssl_verify_flags

    # CA bundle for server certificate validation
    cafile = os.path.join(package_data, "ca-bundle.crt")

    context.load_verify_locations(cafile=cafile)

    if ssl.HAS_ALPN:
        context.set_alpn_protocols(
            [
                "http/1.1"
            ]
        )

    if python_version >= 3.7:
        # Only available in Python 3.7 or higher
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3

        # Disable using 'commonName' for SSLContext.check_hostname
        # when the 'subjectAltName' extension isn't available.
        context.hostname_checks_common_name = False

    if python_version >= 3.8:
        # Signal to server support for PHA in TLS 1.3.
        context.post_handshake_auth = True

    return context

# Default options for HTTP requests
class HTTPOptions:
    
    def __init__(
        self,
        timeout=None,
        max_redirects=None,
        max_body_size=None,
        headers=None,
        ssl_context=None
    ):
        self.timeout = 8 if timeout is None else timeout
        self.max_redirects = 13 if max_redirects is None else max_redirects
        self.max_body_size = 100000 if max_body_size is None else max_body_size
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Connection": "close",
            "User-Agent": f"Unalix/{__version__} (+https://github.com/AmanoTeam/Unalix)"
        } if headers is None else headers
        self.ssl_context = create_ssl_context() if ssl_context is None else ssl_context

# Path to directory containing the package data
package_data = os.path.join(
    os.path.dirname(__file__), "package_data"
)

# Regex patterns for tracking fields removal
data_min = (
    os.path.join(package_data, "data.min.json"),
    os.path.join(package_data, "unalix-data.min.json"),
)

# Regex patterns for extracting redirect URLs from HTML documents
body_redirects = (
    os.path.join(package_data, "body_redirects.json"),
)

# Domains that require cookies to work properly
cookie_required = (
    os.path.join(package_data, "cookies_required.json"),
)

allowed_cookies = []

for file in cookie_required:
    with open(file=file, mode="r", encoding="utf-8") as jfile:
        content = jfile.read()
        allowed_cookies += json.loads(content)

httpopt = HTTPOptions()
