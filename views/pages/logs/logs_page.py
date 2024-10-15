from base import QWidgetBase

from .logs_page_css import STYLES
from .logs_page_ui import LogsPageView


class LogsPage(QWidgetBase):
    """
    A controller class for managing the Logs page, which handles logging output and
    interacts with the LogsPageView.

    Attributes:
        ui (LogsPageView): The view class responsible for displaying the logs.
        layout (QVBoxLayout): The layout containing the UI components for the logs page.
    """

    def __init__(self):
        super().__init__()

        self.setStyleSheet(STYLES)
        # Initialize the UI for the LogsPage
        self.ui = LogsPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        # Connect the logger's send_log signal to the UI's log display update method
        self.logger.send_log.connect(self.ui.update_log_display)
