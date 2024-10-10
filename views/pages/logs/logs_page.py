from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from components.toasts import QToast
from models import LogSettingsModel

from .logs_page_css import STYLES
from .logs_page_ui import LogsPageView


class LogsPage(QWidgetBase):
    send_settings = Signal(str, str, int, int, int, bool)

    def __init__(self):
        super().__init__()

        self.setStyleSheet(STYLES)

        self.ui = LogsPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.logger.send_log.connect(self.ui.update_log_display)
