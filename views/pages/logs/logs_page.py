import os

from PySide6.QtCore import Signal, Slot

from components.toasts import QToast
from components.utils import QWidgetBase
from models import LogSettingsModel

from .logs_page_ui import LogsPageView


class LogsPage(QWidgetBase):
    send_settings = Signal(str, str, int, int, int, bool)

    def __init__(self):
        super().__init__()

        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "logs_page.css")

        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui = LogsPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.logger.send_log.connect(self.ui.update_log_display)
