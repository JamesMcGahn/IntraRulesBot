class StoppedRequestException(Exception):
    """Rule has duplicate name."""

    def __init__(self, message=None):
        if message is None:
            message = "Stop Requested"
        super().__init__(message)
