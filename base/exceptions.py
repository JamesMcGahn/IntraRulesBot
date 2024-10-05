class DuplicateRuleName(Exception):
    """Rule has duplicate name."""

    def __init__(self, message=None):
        if message is None:
            message = "An error occurred"
        super().__init__(message)