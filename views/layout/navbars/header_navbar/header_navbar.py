import json
import os
import uuid

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFileDialog

from base import QWidgetBase
from components.dialogs import ErrorDialog, MessageDialog
from models import RulesModel
from services.validator import SchemaValidator

from .header_navbar_ui import HeaderNavBarView


class HeaderNavBar(QWidgetBase):
    hamburger_signal = Signal(bool)

    load_rules = Signal(list)

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

        self.val = SchemaValidator("./schemas", "/schemas/rules")
        self.total_errors = 0
        self.rules_errors = []

        self.json_decode_error = ""
        self.file_failed = False

        self.rules = RulesModel()
        self.load_rules.connect(self.rules.add_rules)

    def hamburger_icon_btn_toggled(self):
        self.hamburger_signal.emit(self.ui.hamburger_icon_btn.isChecked())

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
            self.logging(f"Opening file - {file_name} to load json data.", "INFO")
            try:
                self.total_errors = 0
                self.rules_errors = []
                with open(file_name, "r") as file:
                    data = json.load(file)

                rules = data.get("rules", [])

                for index, rule in enumerate(rules):
                    rule_error = []
                    validate = self.val.get_validator()
                    for error in validate.iter_errors(rule):
                        rule_error.append(error)
                        self.total_errors = self.total_errors + 1

                        failed_feild, error_path_msg, error_msg = (
                            self.val.format_validation_error(error)
                        )
                        self.logging(
                            f"In file {file_name} - {error_path_msg} - Field: {failed_feild} - Reason: {error_msg}",
                            "ERROR",
                            True,
                        )

                    rule_name = rule.get("rule_name", None)
                    if not rule_name:
                        rule_name = f"Rule {index + 1}: Rule Has No Name"
                    else:
                        rule_name = f"Rule {index + 1}: {rule_name}"

                    error_dict = {"errors": rule_error, "rule_name": rule_name}
                    self.rules_errors.append(error_dict)
                    self.file_failed = True

                if self.total_errors == 0:
                    data = data["rules"]
                    for rule in data:
                        rule["guid"] = str(uuid.uuid4())
                    self.logging(
                        f"0 errors found - {file_name} in JSON file. Sending Data to Rules Model",
                        "INFO",
                        True,
                    )
                    self.load_rules.emit(data)
                else:
                    err_dialog = ErrorDialog(self.rules_errors)
                    err_dialog.show()

            except json.JSONDecodeError as e:
                self.file_failed = True
                json_error = MessageDialog("Json Erorr", str(e))
                json_error.show()
                self.logging(
                    f"JSON error in the file {file_name} - {str(e)}", "ERROR", True
                )
            except Exception as e:
                self.file_failed = True
                gen_error = MessageDialog("Erorr Loading File", str(e))
                gen_error.show()
                self.logging(f"Error in the file {file_name} - {str(e)}", "ERROR", True)
