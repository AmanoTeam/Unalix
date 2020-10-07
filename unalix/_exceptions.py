class InvalidURL(Exception):
    """URL is improperly formed or cannot be parsed."""
    def __init__(self, message: str) -> None:
        super().__init__(message)

class InvalidScheme(Exception):
    """URL has a invalid or unknown scheme."""
    def __init__(self, message: str) -> None:
        super().__init__(message)

class InvalidList(Exception):
    """This is not a valid list.

    It probably has no items or is not actually an object of the 'list' class.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
