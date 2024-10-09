import json
import os

from PySide6.QtCore import Signal

from base import QWidgetBase
from components.dialogs import ErrorDialog
from keys import keys
from models import RulesModel
from rulerunner import RuleRunnerThread
from services.validator import SchemaValidator

from .rules_page_ui import RulesPageView


class RulesPage(QWidgetBase):
    send_rules = Signal(list)

    def __init__(self):
        super().__init__()
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "rules_page.css")

        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui = RulesPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        self.forms_errors = []
        self.total_errors = 0
        self.setGraphicsEffect(None)
        self.rulesModel = RulesModel()

        # Signal / Slot Connections
        self.rulesModel.data_changed.connect(self.ui.rules_changed)
        self.ui.download.clicked.connect(self.save_rules_to_file)
        self.ui.validate.clicked.connect(self.validate_rules)
        self.ui.save.clicked.connect(self.save_rules_to_system)
        self.send_rules.connect(self.ui.rules_changed)
        self.ui.validate_open_dialog.clicked.connect(self.display_errors_dialog)

        # with open("avaya_rules.json") as f:
        #     config_data = json.load(f)

        # start = QPushButton("Start")
        # main_layout.addWidget(start)
        # start.clicked.connect(self.start_thread)

        self.val = SchemaValidator("./schemas", "/schemas/main")
        self.check_for_saved_rules()

    def display_errors_dialog(self):
        add = ErrorDialog(self.forms_errors)
        self.ui.set_hidden_errors_dialog_btn(False)
        add.show()

    def check_for_saved_rules(self):
        self.send_rules.emit(self.rulesModel.rules)

    def progress_received(self, currentRuleIndex, totalRules):
        # TODO: Progress bar
        print(f"rule - {currentRuleIndex} - {totalRules}")

    def start_thread(self):
        config_data = None
        with open("avaya_rules.json") as f:
            config_data = json.load(f)

        self.rule_runner_thread = RuleRunnerThread(
            keys["login"], keys["password"], keys["url"], config_data["rules"]
        )
        self.rule_runner_thread.send_insert_logs.connect(self.logging)
        self.appshutdown.connect(self.rule_runner_thread.close)
        self.rule_runner_thread.progress.connect(self.progress_received)
        self.rule_runner_thread.start()

    def validate_rules(self):

        rules = []
        rules_with_guid = []

        rules_inputs = self.ui.get_forms()
        self.total_errors = 0
        self.forms_errors = []
        if len(rules_inputs) == 0:
            return (None, None)

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
            rules.append(data)

        if self.total_errors > 0:
            self.ui.validate_feedback.setText(f"Total Errors : {self.total_errors}")
            self.ui.validate_feedback.setIcon(self.ui.error_icon)

            self.display_errors_dialog()
            return (None, None)
        else:
            self.total_errors = 0
            self.forms_errors = []
            self.ui.set_hidden_errors_dialog_btn(True)
            self.ui.validate_feedback.setText("No Errors Found")
            self.ui.validate_feedback.setIcon(self.ui.no_error_icon)
            [rule.pop("errors", None) for rule in rules]
            data = {"rules": rules}
            return (data, rules_with_guid)

    def save_rules_to_file(self):
        if self.ui.get_forms():
            if self.validate_rules() is not None:
                data, _ = self.validate_rules()
                if data:
                    with open("./avaya_user.json", "w") as f:
                        json.dump(data, f, indent=4)
                # TODO Confirmation message - toast

    def save_rules_to_system(self):
        if self.ui.get_forms():
            if self.validate_rules() is not None:
                _, data = self.validate_rules()
                if data:
                    self.rulesModel.save_rules(data)
            else:
                self.rulesModel.save_rules([])
