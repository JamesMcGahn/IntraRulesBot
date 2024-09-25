import logging
import os
import queue
import time
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QObject, Signal

from utils.files import PathManager
from utils.singleton import Singleton

from .log_worker import LogWorker


class Logger(QObject, Singleton):
    send_log = Signal(str)

    def __init__(
        self, filename="./logs/file.log", max_size=5 * 1024 * 1024, backup_count=5
    ):
        """
        Initialize the logger.

        :param filename: The log file path.
        :param max_size: Maximum size (in bytes) of the log file before rolling over.
        :param backup_count: Number of backup files to keep.
        """
        super().__init__()
        self.filename = filename
        self.log_queue = queue.Queue()
        path = PathManager.regex_path(self.filename)
        if not PathManager.path_exists(path["path"], True):
            return

        self.log_worker = LogWorker(self.log_queue, self.filename)
        self.log_worker.log_signal.connect(self.send_logs_out)
        self.log_worker.start()

        # Perform initial cleanup of old logs
        self.cleanup_old_logs()

    def send_logs_out(self, msg):
        self.send_log.emit(msg)

    def insert(self, msg, level="INFO", print_msg=True):

        if print_msg:
            print(msg)

        self.log_queue.put((level, msg))

    def cleanup_old_logs(self):
        """
        Delete log files older than 30 days.
        """
        log_dir = os.path.dirname(self.filename)
        if not os.path.exists(log_dir):
            return

        # Get current time
        current_time = time.time()

        # Iterate through log files in the directory
        for log_file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, log_file)
            # Check if it's a file
            if os.path.isfile(file_path):
                # Get the file's last modification time
                file_age = current_time - os.path.getmtime(file_path)
                # Delete files older than 30 days (30 * 24 * 60 * 60 seconds)
                if file_age > 30 * 24 * 60 * 60:
                    os.remove(file_path)

    def close(self):
        """
        Close the log handlers properly.
        """
        self.log_worker.stop()  # Signal the logging thread to stop
        self.log_worker.quit()  # Stop the thread
        self.log_worker.wait()  # Wait for the thread to finish
        self.log_worker.cleanup()  # Clean up the logger
