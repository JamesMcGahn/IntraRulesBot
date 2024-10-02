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
)

from components.buttons import GradientButton, ToggleButton
from components.helpers import WidgetFactory


class SettingsPageView(QWidget):
    send_creds = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.settings_layout = QVBoxLayout(self)

        outter_layout = WidgetFactory.create_form_box(
            "Application Settings",
            self.settings_layout,
            False,
            object_name="Login-Information",
        )

        inner_layout = WidgetFactory.create_form_box(
            "Logging Settings",
            outter_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58321",
            max_width=400,
        )

        log_file_path_label = QLabel("Folder Path:")
        log_file_path_label.setMaximumWidth(75)
        self.log_file_path = QLineEdit()

        self.log_file_path.setStyleSheet("background-color: #FCFCFC")
        self.log_file_path.setMaximumWidth(187)
        self.select_folder_button = QPushButton()
        self.select_folder_button.setMaximumWidth(52)

        folder_icon = QIcon()
        folder_icon.addFile(":/images/open_folder.png", QSize(), QIcon.Mode.Normal)

        self.select_folder_button.setIcon(folder_icon)
        self.select_folder_button.setIconSize(QSize(50, 20))

        self.select_folder_button.clicked.connect(self.open_folder_dialog)

        row_layout = QHBoxLayout()
        row_layout.addWidget(log_file_path_label)
        row_layout.addWidget(self.log_file_path)
        row_layout.addWidget(self.select_folder_button)
        row_layout.setSpacing(0)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        inner_layout.addRow(row_layout)

        self.log_file_name = WidgetFactory.create_form_input_row(
            "file.log", "Log Filename:", inner_layout
        )
        self.log_file_max_mbs = WidgetFactory.create_form_input_row(
            "5", "Max File Size (mb):", inner_layout, validator=QIntValidator()
        )
        self.log_backup_count = WidgetFactory.create_form_input_row(
            "5", "Log Backup Files:", inner_layout, validator=QIntValidator()
        )
        self.log_keep_files_days = WidgetFactory.create_form_input_row(
            "30", "Keep Log Backup Days:", inner_layout, validator=QIntValidator()
        )
        turnoff_label = QLabel("Turn OFF Console Print")
        self.log_turn_off_print = ToggleButton(active_background_color="#f48320")

        inner_layout.addRow(turnoff_label, self.log_turn_off_print)
        self.save_btn = GradientButton(
            "Save",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58321",
            1,
            3,
        )

        inner_layout.addRow(self.save_btn)

        inner_layout.setAlignment(self.save_btn, Qt.AlignmentFlag.AlignRight)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:

            self.log_file_path.setText(folder)
