from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import ControllerFactory
    from views.components.toasts.qtoast.enums import QTOASTSTATUS
    from services.logger.adapters import LogAdapter
    from PySide6.QtWidgets import QWidget

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from base.enums import UIEVENTTYPE, LOGLEVEL
from services.base.enums import JOBSTATUS

from base.events import UIEvent
from views.components.toasts import QToast
from views.components.toasts.qtoast.enums import QTOASTSTATUS
from base.events import UIEvent, ToastEvent, SchemaErrorDialogEvent

from views.components.dialogs import SchemaErrorDialog


class UIController(QObjectBase):

    def __init__(self, logger: LogAdapter):
        super().__init__()
        self.logger = logger
        self.parent_widget = None

    def set_parent_widget(self, widget: QWidget):
        if self.parent_widget is not None:
            return
        self.parent_widget = widget

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @Slot(object)
    def handle_ui_event(self, event: UIEvent):
        e = event.payload
        if isinstance(e, ToastEvent):

            self.log_with_toast(e.title, e.message, e.log_level, e.toast_level)
        elif isinstance(e, SchemaErrorDialogEvent):
            SchemaErrorDialog(errors=e.errors, parent=self.parent_widget).show()

    def log_with_toast(
        self,
        toast_title: str,
        msg: str,
        log_level: LOGLEVEL = LOGLEVEL.INFO,
        toast_level: QTOASTSTATUS = QTOASTSTATUS.INFORMATION,
        print_msg: bool = True,
    ) -> None:
        """
        Logs a message with the specified log level and shows toast message.
        """
        self.logger(msg, log_level, print_msg)
        QToast(self.parent_widget, toast_level, toast_title, msg).show()
