class QueueNotFound(Exception):
    """Queue Not Found"""

    def __init__(self, message=None):
        if message is None:
            message = "QueueNotFound: queue does not exist."
        super().__init__(message)
