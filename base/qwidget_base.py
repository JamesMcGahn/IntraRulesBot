from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget


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
