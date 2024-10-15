import json
from typing import Optional, Tuple

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QLineEdit, QTextEdit

from base import QWidgetBase
from components.dialogs import ErrorDialog
from models import RulesModel
from models.login import LoginModel
from rulerunner import RuleRunnerThread
from services.event_filter import EventFilter
from services.validator import SchemaValidator

from .rules_page_css import STYLES
from .rules_page_ui import RulesPageView


class RulesPage(QWidgetBase):
    """
    RulesPage is responsible for managing the rules displayed in the UI. It handles
    loading, validating, saving, and copying rule fields. The UI interactions are handled
    through the connected view and model components.

    Signals:
        send_rules (list): Emits the list of rules to the view.
    """

    send_rules = Signal(list)

    def __init__(self):
        """
        Initialize the RulesPage, set up models, connect signals/slots, and load the saved rules.
        """
        super().__init__()

        self.setStyleSheet(STYLES)

        self.ui = RulesPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        self.forms_errors = []
        self.total_errors = 0
        self.setGraphicsEffect(None)
        self.rulesModel = RulesModel()

        self.loginModel = LoginModel()
        self.loginModel.creds_changed.connect(self.update_credentials)
        username, password, url, login_url = self.loginModel.get_creds()
        self.username = username
        self.password = password
        self.url = url
        self.login_url = login_url

        # Signal / Slot Connections
        self.rulesModel.data_changed.connect(self.ui.rules_changed)
        self.ui.download.clicked.connect(self.save_rules_to_file)
        self.ui.validate.clicked.connect(self.validate_rules)
        self.ui.save.clicked.connect(self.save_rules_to_system)
        self.send_rules.connect(self.ui.rules_changed)
        self.ui.validate_open_dialog.clicked.connect(self.display_errors_dialog)
        self.ui.copy_field.clicked.connect(self.on_copy_fields)
        self.ui.start.clicked.connect(self.start_rule_runner)
        self.ui.rules_form_updated.connect(self.apply_event_filter)

        self.val = SchemaValidator("/schemas/main")
        self.check_for_saved_rules()
        self.event_filter = EventFilter()
        self.event_filter.event_changed.connect(self.focus_changed)
        self.apply_event_filter()
        self.focus_object_name = None
        self.focus_object_text = None

    @Slot()
    def apply_event_filter(self):
        for child in self.findChildren(QLineEdit):
            child.setFocusPolicy(Qt.StrongFocus)
            child.installEventFilter(self.event_filter)

    @Slot(str, str)
    def focus_changed(self, obj_name: str, object_text: str) -> None:
        """
        Slot to handle when focus changes between form fields. Updates the current focused
        object's name and text.

        Args:
            obj_name (str): The name of the focused object.
            object_text (str): The text value of the focused object.

        Returns:
            None: This function does not return a value.

        """
        field_name = obj_name.split("**")[0]
        self.focus_object_name = field_name
        self.focus_object_text = object_text

    def on_copy_fields(self) -> None:
        """
        Copy the value from the currently focused field across all rules in the form.

        Returns:
            None: This function does not return a value.
        """
        if self.focus_object_name is not None and self.focus_object_text is not None:
            rules = self.ui.get_forms()

            rule_inputs = [rule.rule_inputs for rule in rules]
            for rule in rule_inputs:
                self.find_field_set_field(rule)

    def find_field_set_field(self, rule: dict) -> None:
        """
        Traverse through the rule structure to find the field corresponding to the currently
        focused field, and set its value accordingly.

        Args:
            rule (dict): A dictionary representing the rule structure with form fields.

        Returns:
            None: This function does not return a value.
        """
        for key, value in rule.items():
            if key == self.focus_object_name:
                if isinstance(value, QLineEdit) or isinstance(value, QTextEdit):
                    value.setText(self.focus_object_text)
            elif isinstance(value, dict):
                self.find_field_set_field(value)
            elif isinstance(value, list):
                [self.find_field_set_field(item) for item in value]

    @Slot(str, str, str, str)
    def update_credentials(
        self, username: str, password: str, url: str, login_url: str
    ) -> None:
        """
        Slot to receive the user credentials used for rule processing and validation.

        Args:
            username (str): The username for login.
            password (str): The password for login.
            url (str): The base URL.
            login_url (str): The URL used for login.

        Returns:
            None: This function does not return a value.
        """
        self.username = username
        self.password = password
        self.url = url
        self.login_url = login_url

    def display_errors_dialog(self) -> None:
        """
        Display the error dialog if validation errors are found in the form fields.

        Returns:
            None: This function does not return a value.
        """
        add = ErrorDialog(self.forms_errors)
        self.ui.set_hidden_errors_dialog_btn(False)
        add.show()

    def check_for_saved_rules(self) -> None:
        """
        Check if there are any saved rules and emit them to the view.

        Returns:
            None: This function does not return a value.
        """
        self.send_rules.emit(self.rulesModel.rules)

    def start_rule_runner(self) -> None:
        """
        Start the rule processing thread if the forms are valid and all credentials are provided.

        Returns:
            None: This function does not return a value.
        """
        if self.ui.get_forms():

            if None in (
                self.username,
                self.password,
                self.url,
                self.login_url,
            ):
                self.log_with_toast(
                    "Missing Login Information",
                    "Please enter the login information in the Login Information Page.",
                    "WARN",
                    "WARN",
                    True,
                    self,
                )

                return

            data, _ = self.validate_rules()

            if data:
                self.rule_runner_thread = RuleRunnerThread(
                    self.username,
                    self.password,
                    self.login_url,
                    self.url,
                    data["rules"],
                )
                self.rule_runner_thread.send_insert_logs.connect(self.logging)
                self.appshutdown.connect(self.rule_runner_thread.close)
                self.ui.stop.clicked.connect(self.rule_runner_thread.stop)
                self.rule_runner_thread.progress.connect(self.ui.set_progress_bar)
                self.rule_runner_thread.start()

    def validate_rules(self) -> Tuple[Optional[dict], Optional[list]]:
        """
        Validate all the rules in the form, returning a tuple with the valid rule data and
        the list of rules with GUIDs.

        Returns:
            tuple: (data, rules_with_guid)
                   - data (dict): The valid rules data.
                   - rules_with_guid (list): The list of rules with GUIDs.
                   Returns (None, None) if there are validation errors.
        """

        rules = []
        rules_with_guid = []

        rules_inputs = self.ui.get_forms()
        self.total_errors = 0
        self.forms_errors = []
        if len(rules_inputs) == 0:
            return (None, None)
        self.logging("Starting Rules Validation", "INFO", True)
        for index, rule in enumerate(rules_inputs):

            error_count, form_errors, data = rule.validate_form()

            rule_name = data.get("rule_name", None)
            if not rule_name:
                rule_name = f"Rule {index + 1}: Rule Has No Name"
            else:
                rule_name = f"Rule {index + 1}: {rule_name}"

            self.total_errors = self.total_errors + error_count

            error_dict = {"errors": form_errors, "rule_name": rule_name}

            self.forms_errors.append(error_dict)
            rules_with_guid.append(data)
            data_copy = data.copy()
            del data_copy["guid"]
            rules.append(data_copy)

        if self.total_errors > 0:
            self.ui.validate_feedback.setText(f"Total Errors : {self.total_errors}")
            self.log_with_toast(
                "Validation Failed",
                f"Total Errors : {self.total_errors}",
                "WARN",
                "WARN",
                True,
                self,
            )
            self.ui.validate_feedback.setIcon(self.ui.error_icon)

            self.display_errors_dialog()
            return (None, None)
        else:
            self.log_with_toast(
                "Validation Succeeded",
                "Validation Successful. Total Errors : 0",
                "INFO",
                "SUCCESS",
                True,
                self,
            )
            self.total_errors = 0
            self.forms_errors = []
            self.ui.set_hidden_errors_dialog_btn(True)
            self.ui.validate_feedback.setText("No Errors Found")
            self.ui.validate_feedback.setIcon(self.ui.no_error_icon)
            [rule.pop("errors", None) for rule in rules]
            data = {"rules": rules}
            return (data, rules_with_guid)

    def save_rules_to_file(self) -> None:
        """
        Save the validated rules to a JSON file selected by the user. It ensures the file has
        a `.json` extension.

        Returns:
            None: This function does not return a value.
        """
        if self.ui.get_forms():
            data, _ = self.validate_rules()
            if data:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save JSON File",
                    "",
                    "JSON Files (*.json);;All Files (*)",
                )
                if file_path:
                    # Ensure the file has a .json extension
                    if not file_path.endswith(".json"):
                        file_path += ".json"

                    with open(file_path, "w") as f:
                        json.dump(data, f, indent=4)
                    self.log_with_toast(
                        "File Saved",
                        "Rules JSON File Saved Successfully.",
                        "INFO",
                        "SUCCESS",
                        True,
                        self,
                    )

    def save_rules_to_system(self) -> None:
        """
        Save the validated rules to the internal system storage.

        Returns:
            None: This function does not return a value.
        """
        if self.ui.get_forms():
            _, data = self.validate_rules()
            if data:
                self.rulesModel.save_rules(data)
                self.log_with_toast(
                    "Rules Saved",
                    "Rules Saved Successfully.",
                    "INFO",
                    "SUCCESS",
                    True,
                    self,
                )
        else:
            self.rulesModel.save_rules([])
