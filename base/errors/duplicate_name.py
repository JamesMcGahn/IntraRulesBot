class DuplicateNameException(Exception):
    """Rule has duplicate name."""

    def __init__(self, message=None):
        if message is None:
            message = "DuplicateNameException: name already exists."
        super().__init__(message)
