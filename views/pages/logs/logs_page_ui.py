from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from components.helpers import WidgetFactory
from components.layouts import ScrollArea
from .logs_page_css import SCROLL_AREA_STYLES

class LogsPageView(QWidget):
    """
    A UI component that represents the logs display page.

    Signals:
        send_creds (Signal[str, str, str, str]): A placeholder signal that may be used
            for future functionality to send credentials.

    Attributes:
        log_display (QTextEdit): A text edit widget used to display log entries.
    """

    send_creds = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the UI components of the log page, including the layout and
        the text display for logs.

        Returns:
            None: This function does not return a value.
        """
        self.settings_layout = QVBoxLayout(self)

        outter_layout = WidgetFactory.create_form_box(
            "Logs",
            self.settings_layout,
            False,
            object_name="Logs-Information",
            title_color="#fcfcfc",
        )

        inner_layout = WidgetFactory.create_form_box(
            "",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
        )
        # Text edit widget for displaying logs
        self.log_display = QTextEdit()
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        # Scroll area for the log display
        scroll_area = ScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.log_display)
        scroll_area.setMinimumWidth(500)
        scroll_area.setStyleSheet(SCROLL_AREA_STYLES)
        inner_layout.addRow(scroll_area)

    def update_log_display(self, log: str) -> None:
        """
        Appends a new log entry to the log display.

        Args:
            log (str): The log entry to be appended.

        Returns:
            None: This function does not return a value.
        """
        self.log_display.append(log)
