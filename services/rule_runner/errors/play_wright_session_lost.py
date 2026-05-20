class PlaywrightSessionLostException(Exception):
    """Rule has duplicate name."""

    def __init__(self, message=None):
        if message is None:
            message = "Playwright session lost"
        super().__init__(message)
