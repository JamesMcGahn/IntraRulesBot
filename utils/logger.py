import logging
import os
import time
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import Signal

from .files import PathManager
from .singleton import Singleton


class Logger(Singleton):
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
        self.filename = filename
        self.format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        path = PathManager.regex_path(self.filename)
        if not PathManager.path_exists(path["path"], True):
            return

        # Set up the rotating file handler
        self.logfile = RotatingFileHandler(
            self.filename, maxBytes=max_size, backupCount=backup_count
        )
        self.logfile.setFormatter(self.format)
        self.log = logging.getLogger(self.filename)
        # default level INFO
        self.log.setLevel(logging.INFO)
        self.log.addHandler(self.logfile)

        # Perform initial cleanup of old logs
        self.cleanup_old_logs()

    def insert(self, msg, level="INFO", print_msg=True):
        current_time_str = time.asctime(time.localtime())

        if print_msg:
            print(msg)

        if level == "INFO":
            self.log.info(msg)
        elif level == "ERROR":
            self.log.error(msg)
        elif level == "WARNING":
            self.log.warning(msg)
        else:
            raise ValueError("Unknown logging level")

        self.send_log(f"{current_time_str} {level} {msg}")

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
        self.log.removeHandler(self.logfile)
        self.logfile.close()
