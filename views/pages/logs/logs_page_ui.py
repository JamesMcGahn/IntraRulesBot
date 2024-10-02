from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QScrollArea, QTextEdit
)

from components.buttons import GradientButton, ToggleButton
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
            title_color="#fcfcfc"
        )

        inner_layout = WidgetFactory.create_form_box(
            "",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58321",
           
        )

        self.log_display = QTextEdit("testesdfelf.widgsdf")
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        scroll_area = ScrollArea(self)
        scroll_area.setWidgetResizable(True)  # Allow the scroll area to resize with the window
        scroll_area.setWidget(self.log_display)  # Set the QTextEdit as the scroll area widget
        # scroll_area.setFixedHeight(25)
        # scroll_area.setFixedWidth(400)
        # Add the scroll area to the form layout
        inner_layout.addRow(scroll_area)


        


    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:

            self.log_file_path.setText(folder)