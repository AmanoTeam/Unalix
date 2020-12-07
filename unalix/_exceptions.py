class InvalidURL(Exception):
    """URL is improperly formed or cannot be parsed."""
    def __init__(self, message, url):
        self.url = url
        super().__init__(message)


class InvalidScheme(Exception):
    """URL has a invalid or unknown scheme."""
    def __init__(self, message, url):
        self.url = url
        super().__init__(message)


class TooManyRedirects(Exception):
    """The request exceeded maximum allowed redirects."""
    def __init__(self, message, url):
        self.url = url
        super().__init__(message)


class ConnectError(Exception):
    """An error occurred during the request."""
    def __init__(self, message, exception, url):
        self.exception = exception
        self.url = url
        super().__init__(message)

