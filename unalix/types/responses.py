from .objects import Dict

class Response(Dict):

    def __init__(
        self,
        http_version,
        status_code,
        status_message,
        headers,
        body
    ):
        self.http_version = http_version
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers
        self.body = body

