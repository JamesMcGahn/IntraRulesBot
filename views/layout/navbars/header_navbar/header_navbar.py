import json
import uuid

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFileDialog

from base import QWidgetBase
from components.dialogs import ErrorDialog, MessageDialog
from models import RulesModel
from services.validator import SchemaValidator

from .header_navbar_css import STYLES
from .header_navbar_ui import HeaderNavBarView


class HeaderNavBar(QWidgetBase):
    """
    HeaderNavBar is the controller for the header navigation bar, managing user interactions such as
    toggling the hamburger menu and loading JSON files to validate rules.

    Signals:
        hamburger_signal (Signal[bool]): Emitted when the hamburger menu button is toggled.
        load_rules (Signal[list]): Emitted to load rules into the RulesModel.

    Attributes:
        ui (HeaderNavBarView): The view component that defines the layout and widgets.
        val (SchemaValidator): Validator used to validate the JSON file against the rules schema.
        total_errors (int): Total count of errors found during JSON validation.
        rules_errors (list): List of rule validation errors.
        json_decode_error (str): Error message when JSON decoding fails.
        file_failed (bool): Flag indicating if loading the file failed.
        rules (RulesModel): Model for managing rules.
    """

    hamburger_signal = Signal(bool)
    load_rules = Signal(list)

    def __init__(self):
        """
        Initializes the HeaderNavBar, sets up the view and connections, and prepares the rule validation.
        """
        super().__init__()
        self.setObjectName("header_widget")
        self.setMaximumSize(QSize(16777215, 175))
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(STYLES)
        # View setup
        self.ui = HeaderNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        # Connect signals
        self.ui.hamburger_icon_btn.toggled.connect(self.hamburger_icon_btn_toggled)
        self.ui.open_file_btn.clicked.connect(self.open_json_file)
        # Validator and rules model
        self.val = SchemaValidator("/schemas/rules")
        self.total_errors = 0
        self.rules_errors = []

        self.json_decode_error = ""
        self.file_failed = False

        self.rules = RulesModel()
        self.load_rules.connect(self.rules.add_rules)

    def hamburger_icon_btn_toggled(self) -> None:
        """
        Slot for handling hamburger button toggle events. Emits the hamburger_signal.

        Returns:
            None: This function does not return a value.
        """
        self.hamburger_signal.emit(self.ui.hamburger_icon_btn.isChecked())

    def open_json_file(self) -> None:
        """
        Opens a file dialog to select a JSON file, validates its content against the rules schema,
        and emits the valid data to the RulesModel. Displays errors if validation fails.

        Returns:
            None: This function does not return a value.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
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
