from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from components.toasts import QToast
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

        # TODO: Use a method on UI to set values
        self.ui.log_file_path.setText(log_file_path)
        self.ui.log_file_name.setText(log_file_name)
        self.ui.log_file_max_mbs.setText(str(log_file_max_mbs))
        self.ui.log_backup_count.setText(str(log_backup_count))
        self.ui.log_keep_files_days.setText(str(log_keep_files_days))
        self.ui.log_turn_off_print.setChecked(log_turn_off_print)

    def save_log_settings(self):

        folder_path = self.ui.log_file_path.text()
        if not folder_path.endswith("/"):
            folder_path += "/"

        # TODO: Use a method on UI to set values
        self.ui.log_file_path.setText(folder_path)

        self.send_settings.emit(
            folder_path,
            self.ui.log_file_name.text(),
            int(self.ui.log_file_max_mbs.text()),
            int(self.ui.log_backup_count.text()),
            int(self.ui.log_keep_files_days.text()),
            self.ui.log_turn_off_print.isChecked(),
        )
        self.logging("Saving Logging Settings", "INFO")

    @Slot()
    def success_save(self):
        QToast(self, "success", "Saved Successful", "Log Settings Saved.")
        self.logging("Logger Settings Saved Successful", "INFO")
