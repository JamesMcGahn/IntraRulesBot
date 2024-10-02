import logging
import os
import queue
import threading
import time
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal, Slot


class LogWorker(QThread):
    log_signal = Signal(str)

    def __init__(
        self,
        log_file_path,
        log_file_name,
        log_file_max_mbs,
        log_backup_count,
        log_keep_files_days,
        log_turn_off_print,
    ):
        super().__init__()
        self.log_queue = queue.Queue()
        self.log_file_path = log_file_path
        self.log_file_name = log_file_name
        self.log_file_max_mbs = log_file_max_mbs
        self.log_backup_count = log_backup_count
        self.log_keep_files_days = log_keep_files_days
        self.log_turn_off_print = log_turn_off_print

        self.stop_event = False
        self.mutex = QMutex()
        self.setup_logging()

    def setup_logging(self):
        complete_path = self.log_file_path + self.log_file_name
        self.logger = logging.getLogger(complete_path)
        self.logger.setLevel(logging.INFO)
        if not isinstance(self.log_file_max_mbs, int):
            self.log_file_max_mbs = 5
        if not isinstance(self.log_backup_count, int):
            self.log_file_max_mbs = 5

        if not self.logger.handlers:
            logfile = RotatingFileHandler(
                complete_path,
                maxBytes=self.log_file_max_mbs * 1024 * 1024,
                backupCount=self.log_backup_count,
            )
            logfile.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            self.logger.addHandler(logfile)
            self.insert_log(
                (
                    "INFO",
                    f"Starting LogWorker Thread: {threading.get_ident()} - {self.thread()}",
                    True,
                )
            )

    @Slot(tuple)
    def insert_log(self, log):
        level, msg, print_msg = log

        if level not in ["INFO", "WARN", "ERROR"]:
            level = "INFO"

        if print_msg and not self.log_turn_off_print:
            print(log)

        self.log_queue.put((level, msg))

    def run(self):
        while not self.stop_event or not self.log_queue.empty():

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
