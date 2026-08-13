class ProviderNotFound(Exception):
    """Queue Not Found"""

    def __init__(self, message=None):
        if message is None:
            message = "ProviderNotFound: provider does not exist."
        super().__init__(message)
