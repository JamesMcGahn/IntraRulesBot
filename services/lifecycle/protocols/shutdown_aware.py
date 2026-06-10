from PySide6.QtCore import Signal
from typing import Protocol


class ShutdownAware(Protocol):
    shutdown_ready: Signal

    def request_app_shutdown(self) -> bool:
        """
        Returns:
            True: shutdown may continue immediately.
            False: service is stopping asynchronously and will emit shutdown_ready.
        """
        ...
