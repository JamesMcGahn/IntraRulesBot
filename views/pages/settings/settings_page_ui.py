from typing import Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from __version__ import __version__
from components.buttons import EditorActionButton, GradientButton, ToggleButton
from components.helpers import WidgetFactory


class SettingsPageView(QWidget):
    """
    A UI component that represents the Settings Page.
    SettingsPageView manages the UI elements for displaying and editing application settings,
    particularly related to logging configuration. It allows users to input settings, choose
    a folder for log storage, and save the configuration.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Setup the UI elements for the settings page, including the logging settings form,
        folder path selection, log file settings, and a save button.
        Connects signals for interactive components like folder selection.

        Returns:
            None: This function does not return a value.
        """
        self.settings_layout = QVBoxLayout(self)

        outter_layout = WidgetFactory.create_form_box(
            "Application Settings",
            self.settings_layout,
            False,
            object_name="Settings-Information",
            title_color="#fcfcfc",
        )

        inner_h_layout = QHBoxLayout()

        inner_layout = WidgetFactory.create_form_box(
            "Logging Settings",
            inner_h_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            max_width=400,
            title_color="#fcfcfc",
            title_font_size=13,
        )

        # Log Settings Fields
        # Folder path input and selection button
        log_file_path_label = QLabel("Folder Path:")
        self.log_file_path = QLineEdit()
        self.log_file_path.setStyleSheet("background-color: #FCFCFC")
        self.select_folder_button = EditorActionButton("")
        self.select_folder_button.setMaximumWidth(30)

        WidgetFactory.create_icon(
            self.select_folder_button,
            ":/images/open_folder_on.png",
            50,
            20,
            True,
            ":/images/open_folder_off.png",
            False,
        )

        self.select_folder_button.clicked.connect(self.open_folder_dialog)
        # Add folder input and button to row
        row_layout = QHBoxLayout()
        row_layout.addWidget(self.log_file_path)
        row_layout.addWidget(self.select_folder_button)
        row_layout.setSpacing(0)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        inner_layout.addRow(log_file_path_label, row_layout)

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

        # Save button
        self.save_btn = GradientButton(
            "Save",
            "black",
            [(0.05, "#FEB220"), (0.50, "#f58220"), (1, "#f58220")],
            "#f58220",
            1,
            3,
        )

        inner_layout.addRow(self.save_btn)

        inner_layout.setAlignment(self.save_btn, Qt.AlignmentFlag.AlignRight)

        inner_h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        outter_layout.addRow(inner_h_layout)

        # Display version at the bottom
        version = QLabel(f"Version:{__version__}")
        version.setObjectName("version")
        vertical_spacer = QSpacerItem(
            2, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.settings_layout.addItem(vertical_spacer)
        self.settings_layout.addWidget(version)

    def set_log_settings(
        self,
        log_file_path,
        log_file_name,
        log_file_max_mbs,
        log_backup_count,
        log_keep_files_days,
        log_turn_off_print,
    ) -> None:
        """
        Sets the log settings in the UI fields with the provided values.

        Args:
            log_file_path (str): The path where log files will be saved.
            log_file_name (str): The name of the log file.
            log_file_max_mbs (int): Maximum size of the log file in megabytes.
            log_backup_count (int): Number of backup log files to keep.
            log_keep_files_days (int): Number of days to retain backup logs.
            log_turn_off_print (bool): Whether to turn off console log printing.

        Returns:
            None: This function does not return a value.
        """

        self.log_file_path.setText(log_file_path)
        self.log_file_name.setText(log_file_name)
        self.log_file_max_mbs.setText(str(log_file_max_mbs))
        self.log_backup_count.setText(str(log_backup_count))
        self.log_keep_files_days.setText(str(log_keep_files_days))
        self.log_turn_off_print.setChecked(log_turn_off_print)

    def get_log_settings(self) -> Tuple[str, str, int, int, int, bool]:
        """
        Retrieves the current log settings from the form fields, including folder path,
        log file name, file size limits, and other log configuration settings.

        Returns:
            Tuple[str, str, int, int, int, bool]: A tuple containing:
                - folder_path (str): The path where logs are stored, ensuring it ends with '/'.
                - log_file_name (str): The name of the log file.
                - log_file_max_mbs (int): Maximum size of the log file in megabytes.
                - log_backup_count (int): Number of backup log files to keep.
                - log_keep_files_days (int): Number of days to retain backup logs.
                - log_turn_off_print (bool): Whether to turn off console log printing.
        """
        folder_path = self.log_file_path.text()
        if not folder_path.endswith("/"):
            folder_path += "/"

        self.log_file_path.setText(folder_path)

        return (
            folder_path,
            self.log_file_name.text(),
            int(self.log_file_max_mbs.text()),
            int(self.log_backup_count.text()),
            int(self.log_keep_files_days.text()),
            self.log_turn_off_print.isChecked(),
        )

    def open_folder_dialog(self) -> None:
        """
        Opens a dialog for the user to select a folder for storing log files.
        Once a folder is selected, the path is updated in the corresponding input field.

        Returns:
            None: This function does not return a value.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:

            self.log_file_path.setText(folder)
