from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from models import LogSettingsModel

from .settings_page_css import STYLES
from .settings_page_ui import SettingsPageView


class SettingsPage(QWidgetBase):
    send_settings = Signal(str, str, int, int, int, bool)

    def __init__(self):
        super().__init__()

        self.setStyleSheet(STYLES)

        self.ui = SettingsPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.save_btn.clicked.connect(self.save_log_settings)

        self.settings = LogSettingsModel()
        self.settings.success.connect(self.success_save)
        self.send_settings.connect(self.settings.save_log_settings)

        (
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
        ) = self.settings.get_log_settings()
        self.ui.set_log_settings(
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
        )

    def save_log_settings(self):
        (
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
        ) = self.ui.get_log_settings()
        self.logging("Saving Logging Settings", "INFO")
        self.send_settings.emit(
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
        )

    @Slot()
    def success_save(self):
        """
        Slot that gets called when the credentials are successfully saved.
        Displays a log message with a success toast notification.

        Returns:
            None: This function does not return a value.
        """
        self.log_with_toast(
            "Log Settings Saved.",
            "Logger Settings Saved Successful",
            "INFO",
            "SUCCESS",
            True,
            self,
        )
