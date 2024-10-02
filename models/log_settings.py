from PySide6.QtCore import QObject, Signal, Slot

from services.settings import AppSettings
from utils.singletons import QSingleton


class LogSettingsModel(QObject, metaclass=QSingleton):
    log_setting_changed = Signal(str, str, int, int, int, bool)
    success = Signal()

    def __init__(self):
        super().__init__()
        self.log_file_path = "./logs/"
        self.log_file_name = "file.log"
        self.log_file_max_mbs = 5
        self.log_backup_count = 5
        self.log_keep_files_days = 30
        self.log_turn_off_print = False

        self.settings = AppSettings()
        self.init_logs_settings()

    def get_log_settings(self):
        return (
            self.log_file_path,
            self.log_file_name,
            self.log_file_max_mbs,
            self.log_backup_count,
            self.log_keep_files_days,
            self.log_turn_off_print,
        )

    @Slot(str, str, int, int, int, bool)
    def save_log_settings(
        self,
        log_file_path,
        log_file_name,
        log_file_max_mbs,
        log_backup_count,
        log_keep_files_days,
        log_turn_off_print,
    ):
        self.log_file_path = log_file_path
        self.log_file_name = log_file_name
        self.log_file_max_mbs = log_file_max_mbs
        self.log_backup_count = log_backup_count
        self.log_keep_files_days = log_keep_files_days
        self.log_turn_off_print = log_turn_off_print

        self.settings.begin_group("logs_settings")
        self.settings.set_value("log_file_path", log_file_path)
        self.settings.set_value("log_file_name", log_file_name)
        self.settings.set_value("log_backup_count", log_backup_count)
        self.settings.set_value("log_file_max_mbs", log_file_max_mbs)
        self.settings.set_value("log_keep_files_days", log_keep_files_days)
        self.settings.set_value("log_turn_off_print", log_turn_off_print)
        self.settings.end_group()

        self.log_setting_changed.emit(
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
        )
        self.success.emit()

    def init_logs_settings(self):
        self.settings.begin_group("logs_settings")
        self.log_file_path = self.settings.get_value("log_file_path", "./logs/")
        self.log_file_name = self.settings.get_value("log_file_name", "file.log")
        self.log_backup_count = self.settings.get_value("log_backup_count", 5)
        self.log_file_max_mbs = self.settings.get_value("log_file_max_mbs", 5)
        self.log_keep_files_days = self.settings.get_value("log_keep_files_days", 30)
        self.log_turn_off_print = self.settings.get_value(
            "log_turn_off_print", False, bool
        )
        self.settings.end_group()
