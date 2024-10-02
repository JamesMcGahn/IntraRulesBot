import logging
import os
import queue
import time
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QObject, Signal, Slot

from models import LogSettingsModel
from utils.files import PathManager
from utils.singletons import QSingleton

from .log_worker import LogWorker


class Logger(QObject, metaclass=QSingleton):
    send_log = Signal(str)
    submit_log = Signal(tuple)

    def __init__(self):
        """
        Initialize the logger.
        """
        super().__init__()
        self.log_file_path = "./logs/"
        self.log_file_name = "file.log"
        self.log_file_max_mbs = 5
        self.log_backup_count = 5
        self.log_keep_files_days = 30
        self.log_turn_off_print = False
        self.settings = LogSettingsModel()
        self.init_logging_settings()

        self.settings.log_setting_changed.connect(self.log_settings_changed)

        path = PathManager.regex_path(self.log_file_path + self.log_file_name)
        if not PathManager.path_exists(path["path"], True):
            return
            # TODO Notify user the path is bad

        self.start_logging_thread()

        # Perform initial cleanup of old logs
        self.cleanup_old_logs()

    def start_logging_thread(self):
        self.log_worker = LogWorker(
            self.log_file_path,
            self.log_file_name,
            self.log_file_max_mbs,
            self.log_backup_count,
            self.log_keep_files_days,
            self.log_turn_off_print,
        )
        self.log_worker.log_signal.connect(self.send_logs_out)
        self.submit_log.connect(self.log_worker.insert_log)
        self.log_worker.start()

    def init_logging_settings(self):
        (
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
        ) = self.settings.get_log_settings()

        self.log_file_path = log_file_path
        self.log_file_name = log_file_name
        self.log_file_max_mbs = log_file_max_mbs
        self.log_backup_count = log_backup_count
        self.log_keep_files_days = log_keep_files_days
        self.log_turn_off_print = log_turn_off_print

    @Slot(tuple)
    def log_settings_changed(self, settings):
        self.insert(
            "Logging settings changed. Restarting Logger to Apply Settings.", "INFO"
        )
        self.close()
        self.init_logging_settings()
        self.start_logging_thread()

    @Slot()
    def turn_off_print_msg(self, switch):
        self.turn_off_print = switch

    def send_logs_out(self, msg):
        self.send_log.emit(msg)

    @Slot(str, str, bool)
    def insert(self, msg, level="INFO", print_msg=True):

        self.submit_log.emit((level, msg, print_msg))

    def cleanup_old_logs(self):
        """
        Delete log files older than 30 days.
        """

        path = PathManager.regex_path(self.log_file_path + self.log_file_name)
        log_dir = path["path"]
        if not PathManager.path_exists(log_dir, True):
            return
            # TODO Notify user the path is bad

        # Get current time
        current_time = time.time()
        self.insert("Checking For Old Log Files to Clean Up", "INFO")
        # Iterate through log files in the directory
        for log_file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, log_file)
            # Check if it's a file
            if os.path.isfile(file_path):
                # Get the file's last modification time
                file_age = current_time - os.path.getmtime(file_path)
                # Delete files older than 30 days (30 * 24 * 60 * 60 seconds)
                if not isinstance(self.log_keep_files_days, int):
                    self.log_keep_files_days = 30
                if file_age > self.log_keep_files_days * 24 * 60 * 60:
                    os.remove(file_path)
                    self.insert(f"Removing old log file {file_path}", "INFO")

    @Slot(bool)
    def close(self):
        """
        Close the log handlers properly.
        """
        self.insert("Shutting down logging", "INFO", True)
        self.log_worker.stop()  # Signal the logging thread to stop
        self.log_worker.quit()  # Stop the thread
        self.log_worker.wait()  # Wait for the thread to finish
        self.log_worker.cleanup()  # Clean up the logger
