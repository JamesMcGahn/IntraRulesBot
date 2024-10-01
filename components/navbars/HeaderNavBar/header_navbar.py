import json
import os

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from services.validator import SchemaValidator

from .header_navbar_ui import HeaderNavBarView


class HeaderNavBar(QWidget):
    hamburger_signal = Signal(bool)
    send_logs = Signal(str, str, bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("header_widget")
        self.setMaximumSize(QSize(16777215, 175))
        self.setAttribute(Qt.WA_StyledBackground, True)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "header_navbar.css")

        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui = HeaderNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.hamburger_icon_btn.toggled.connect(self.hamburger_icon_btn_toggled)

        self.ui.open_file_btn.clicked.connect(self.open_json_file)

        self.val = SchemaValidator("./schemas", "/schemas/main")
        self.validate_errors = []
        self.json_decode_error = ""
        self.file_failed = False

    def open_json_file(self) -> None:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options,
        )

        if file_name:
            try:
                with open(file_name, "r") as file:
                    data = json.load(file)
                validate = self.val.get_validator()
                self.validate_errors = []
                for error in validate.iter_errors(data):
                    self.file_failed = True
                    self.validate_errors.append(error)
                    failed_feild, error_path_msg, error_msg = (
                        self.val.format_validation_error(error)
                    )
                    self.send_logs.emit(
                        f"In file {file_name} - {error_path_msg} - Field: {failed_feild} - Reason: {error_msg}",
                        "ERROR",
                        True,
                    )
                    self.validate_errors.append(
                        (failed_feild, error_path_msg, error_msg)
                    )

            except json.JSONDecodeError as e:
                self.file_failed = True
                self.send_logs.emit(e, "ERROR", True)

    def hamburger_icon_btn_toggled(self):
        self.hamburger_signal.emit(self.ui.hamburger_icon_btn.isChecked())

        # try:
        # TODO add qdialog to display errors - make reusable to use with config editor
        # if self.file_failed:

        #     QMessageBox.critical(
        #         self,
        #         "Error",
        #         f"Theres an error with your file: \n ",
        #     )
