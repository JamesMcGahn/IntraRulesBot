from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter


class ServiceBase:

    def __init__(self, logger: LogAdapter):
        self.logger = logger

    def _logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)
