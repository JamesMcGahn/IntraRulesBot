from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter

from base.logging_base import LoggingBase
from time import monotonic, sleep


class NetworkThrottle(LoggingBase):
    """Class to throttle requests. Throttle will delay requests based on time of the last request.
    params:
    interval: time between requests in ms
    """

    def __init__(self, logger: LogAdapter, interval: float = 0.5):
        super().__init__(logger)
        self._interval = interval
        self._last_call = 0.0

    def wait(self):
        elapsed = monotonic() - self._last_call

        if elapsed < self._interval:
            wait_time = self._interval - elapsed
            self.logging(
                f"Waiting: {wait_time} seconds. Last request received at {self._last_call}"
            )
            sleep(wait_time)
            self._last_call = monotonic()
