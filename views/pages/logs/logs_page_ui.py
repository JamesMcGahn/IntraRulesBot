from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from components.helpers import WidgetFactory
from components.layouts import ScrollArea


class LogsPageView(QWidget):
    send_creds = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
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
            "#f58321",
        )

        self.log_display = QTextEdit()
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        scroll_area = ScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.log_display)
        scroll_area.setMinimumWidth(500)

        inner_layout.addRow(scroll_area)

    def update_log_display(self, log):
        self.log_display.append(log)
