import logging
import os
import queue
import time
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QThread, Signal


class LogWorker(QThread):
    log_signal = Signal(str)  # Signal to emit log messages

    def __init__(self, log_queue, filename):
        super().__init__()
        self.log_queue = log_queue
        self.filename = filename
        self.stop_event = False
        self.logfile = RotatingFileHandler(
            self.filename, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        self.logfile.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        self.logger = logging.getLogger(self.filename)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.logfile)

    def run(self):
        """Process log messages from the queue."""
        while not self.stop_event or not self.log_queue.empty():
            current_time_str = time.asctime(time.localtime())
            try:
                level, msg = self.log_queue.get(timeout=1)
                if level == "INFO":
                    self.logger.info(msg)
                elif level == "ERROR":
                    self.logger.error(msg)
                elif level == "WARNING":
                    self.logger.warning(msg)
                self.log_queue.task_done()
                self.log_signal.emit(f"{current_time_str} {level} {msg}")
            except queue.Empty:
                continue

    def stop(self):
        """Signal the logging thread to stop."""
        self.stop_event = True

    def cleanup(self):
        """Close the log handler properly."""
        self.logger.removeHandler(self.logfile)
        self.logfile.close()
