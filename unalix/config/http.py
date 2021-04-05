from ..__version__ import __version__

from ..types import Int, Dict


HTTP_HEADERS = Dict({
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Connection": "close",
    "User-Agent": f"Unalix/{__version__} (+https://github.com/AmanoTeam/Unalix)"
})

HTTP_TIMEOUT = Int(8)

HTTP_MAX_REDIRECTS = Int(13)

HTTP_MAX_FETCH_SIZE = Int(1024 * 1024)

