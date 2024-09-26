import threading

from PySide6.QtCore import QObject, Signal


class WorkerClass(QObject):
    send_logs = Signal(str, str, bool)
    finished = Signal()

    def __init__(self):
        super().__init__()

    def logging(self, msg, level="INFO", print_msg=True):
        self.send_logs.emit(msg, level, print_msg)

    def log_thread(self):
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )
