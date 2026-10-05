class QueueFound(Exception):
    """Queue Not Found"""

    def __init__(self, message=None):
        if message is None:
            message = "QueueFound: queue still exists."
        super().__init__(message)
