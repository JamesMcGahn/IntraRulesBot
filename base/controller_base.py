from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter


from PySide6.QtCore import Signal, QObject
from base.enums import UIEVENTTYPE, LOGLEVEL
from base.events import (
    ToastEvent,
    UIEvent,
)
from views.components.toasts.qtoast.enums import QTOASTSTATUS


class ControllerBase(QObject):
    ui_event = Signal(object)

    def __init__(self, logger: LogAdapter):
        super().__init__()
        self.logger = logger

    def _logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def send_toast_failure(self, title, message):
        toast = ToastEvent(
            message=message,
            title=title,
            toast_level=QTOASTSTATUS.ERROR,
            log_level=LOGLEVEL.ERROR,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)

    def send_toast_success(self, title, message):
        toast = ToastEvent(
            message=message,
            title=title,
            toast_level=QTOASTSTATUS.SUCCESS,
            log_level=LOGLEVEL.INFO,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)
