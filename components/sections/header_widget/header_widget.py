import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QWidget

from services.validator import SchemaValidator


class HeaderWidget(QWidget):
    send_logs = Signal(str, str, bool)

    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)
        self.open_btn = QPushButton("Open File")

        main_layout.addWidget(self.open_btn)
        self.open_btn.clicked.connect(self.open_json_file)

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

        # try:
        # TODO add qdialog to display errors - make reusable to use with config editor
        # if self.file_failed:

        #     QMessageBox.critical(
        #         self,
        #         "Error",
        #         f"Theres an error with your file: \n ",
        #     )
