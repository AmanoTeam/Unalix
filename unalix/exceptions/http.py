class UnalixException(Exception):
    
    
    def __init__(
        self,
        message: str,
        url: str
    ):
        self.message = message
        self.url = url
        
        super().__init__(message)


class UnsupportedProtocolError(UnalixException):
    pass


class ConnectError(UnalixException):
    pass


class MaxRetriesError(ConnectError):
    pass


class TooManyRedirectsError(UnalixException):
    pass