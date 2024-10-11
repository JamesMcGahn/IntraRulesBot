from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget

from components.toasts import QToast


class QWidgetBase(QWidget):
    send_logs = Signal(str, str, bool)
    appshutdown = Signal()

    def __init__(self):
        super().__init__()
        from services.logger import Logger

        self.logger = Logger()
        self.send_logs.connect(self.logger.insert)

    @Slot(str, str, bool)
    def logging(self, msg, level="INFO", print_msg=True):
        self.send_logs.emit(msg, level, print_msg)

    @Slot()
    def notified_app_shutting(self):
        self.appshutdown.emit()

    @Slot()
    def log_with_toast(
        self,
        toast_title,
        msg,
        log_level="INFO",
        toast_level="INFO",
        print_msg=True,
        parent=None,
    ):
        self.logging(msg, log_level, print_msg)
        QToast(parent, toast_level, toast_title, msg)
