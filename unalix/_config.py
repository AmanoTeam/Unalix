import asyncio
from http.cookiejar import DefaultCookiePolicy
import json
import os
import platform
import ssl

major, minor, micro = platform.python_version_tuple()
python_version = float(f"{major}.{minor}")

loop = asyncio.get_event_loop()

# Path to directory containing the package data (JSON files)
data = os.path.join(os.path.dirname(__file__), "package_data")

# JSON files containing regex patterns for tracking fields removal (full paths)
paths_data = [
    f"{data}/data.min.json", 
    f"{data}/unalix-data.min.json"
]

# JSON files containing regex patterns for extracting redirect URLs
# from HTML documents (full paths)
paths_redirects = [
	f"{data}/body_redirects.json"
]

# Some of these fields may remain in the URL after tracking"s fields
# removal, so we need to remove or replace them
replacements = [
    (r"(?:%26)+", r"%26"),
    (r"&+", r"&"),
    (r"(?:%3[fF])+", r"%3f"),
    (r"(?:%(?:3[fF]|23)|\?|#|&)+$", r""),
    (r"\?&",  r"?"),
    (r"(?:%(?:3[fF]|26))", r"%3f")
]

# Default timeout for HTTP requests
timeout = 15

# Maximum number of HTTP redirections allowed by default
max_redirects = 25

# Domain names that points to a local address
local_domains = [
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback"
]

# List of allowed schemes
allowed_schemes = ["http", "https"]

# List of allowed mime types
allowed_mimes = [
	"application/mathml-content+xml",
	"application/mathml-presentation+xml",
	"application/vnd.dtg.local.html",
	"application/vnd.pwg-xhtml-print+xml",
	"application/xhtml+xml",
	"text/html",
	"text/javascript"
]

# Default headers for HTTP requests
default_headers = {
    "Accept": ", ".join(allowed_mimes),
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close",
    "Cache-Control": "no-cache, no-store",
    "User-Agent": "Unalix/0.6 (+https://github.com/AmanoTeam/Unalix)"
}

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

# Default options for SSL contexts
ssl_options = (
	ssl.OP_ALL \
	| ssl.OP_NO_SSLv2 \
	| ssl.OP_NO_SSLv3 \
    | ssl.OP_NO_TLSv1 \
	| ssl.OP_NO_TLSv1_1 \
	| ssl.OP_NO_TICKET \
	| ssl.OP_NO_COMPRESSION \
	| ssl.OP_SINGLE_DH_USE \
	| ssl.OP_SINGLE_ECDH_USE
)

# ssl.OP_NO_RENEGOTIATION is not available on Python versions bellow 3.7
if python_version > 3.6:
    ssl_options |= ssl.OP_NO_RENEGOTIATION

# Default verify flags for SSL contexts
ssl_verify_flags = (
	ssl.VERIFY_X509_STRICT \
	| ssl.VERIFY_X509_TRUSTED_FIRST \
	| ssl.VERIFY_DEFAULT
)

# CA bundle for server certificate validation
cafile = f"{data}/ca-bundle.crt"

# CA certs path for server certificate validation
capath = os.path.dirname(cafile)

# Load "arguments.json" and "cookies_required.json" as dicts
with open(f"{data}/arguments.json", mode="r", encoding="utf-8") as arguments:
    arguments = json.loads(arguments.read())

with open(f"{data}/cookies_required.json", mode="r", encoding="utf-8") as cookies_required:
    allowed_cookies = json.loads(cookies_required.read())

# Default policy for cookies: allow all
allow_all_cookies = DefaultCookiePolicy()
allow_all_cookies.set_ok = lambda cookie, request: True

# Default policy for cookies: deny all
deny_all_cookies = DefaultCookiePolicy()
deny_all_cookies.set_ok = lambda cookie, request: False

# Default policy for cookies: allow if needed
allow_cookies_if_needed = DefaultCookiePolicy()
allow_cookies_if_needed.set_ok = lambda cookie, request: (cookie.domain in allowed_cookies)

# Description for command-line script
description = "Remove tracking fields from the given URL and/or unshort it (follow http redirects)."