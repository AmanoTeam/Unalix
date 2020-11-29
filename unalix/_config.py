import json
import os

from ._utils import get_python_version

python_version = get_python_version()

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

# Default timeout for HTTP requests
timeout = 8

# Maximum number of HTTP redirections allowed by default
max_redirects = 13

# List of allowed schemes
allowed_schemes = [
    "http",
    "https"
]

# List of allowed mime types
allowed_mimes = [
    "application/ecmascript",
    "application/mathml-content+xml",
    "application/mathml-presentation+xml",
    "application/vnd.dtg.local.html",
    "application/vnd.pwg-xhtml-print+xml",
    "application/x-ecmascript",
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

# Load "cookies_required.json" as dict
with open(f"{data}/cookies_required.json", mode="r") as file:
    content = file.read()
    allowed_cookies = json.loads(content)
