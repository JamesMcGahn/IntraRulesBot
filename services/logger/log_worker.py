import logging
import os
import queue
import time
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal, Slot


class LogWorker(QThread):
    log_signal = Signal(str)

    def __init__(self, log_queue, filename):
        super().__init__()
        self.log_queue = log_queue
        self.filename = filename
        self.stop_event = False
        self.mutex = QMutex()
        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger(self.filename)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            logfile = RotatingFileHandler(
                self.filename, maxBytes=5 * 1024 * 1024, backupCount=5
            )
            logfile.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            self.logger.addHandler(logfile)

    @Slot(tuple)
    def insert_log(self, log):
        level, msg = log
        self.log_queue.put((level, msg))

    def run(self):
        while not self.stop_event:
            if self.log_queue.empty():
                try:
                    current_time_str = time.asctime(time.localtime())
                    level, msg = self.log_queue.get(timeout=1)
                    with QMutexLocker(self.mutex):
                        if level == "INFO":
                            self.logger.info(msg)
                        elif level == "ERROR":
                            self.logger.error(msg)
                        elif level == "WARNING":
                            self.logger.warning(msg)
                        self.log_signal.emit(f"{current_time_str} {level} {msg}")
                    self.log_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Logging error: {e}")

    def stop(self):
        self.stop_event = True

    def cleanup(self):
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
