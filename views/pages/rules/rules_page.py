import json
import os

from base import QWidgetBase
from keys import keys
from models import RulesModel
from rulerunner import RuleRunnerThread
from services.validator import SchemaValidator

from .rules_page_ui import RulesPageView


class RulesPage(QWidgetBase):

    def __init__(self):
        super().__init__()
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "rules_page.css")

        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui = RulesPageView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.setGraphicsEffect(None)
        self.rulesModel = RulesModel()
        self.rulesModel.data_changed.connect(self.ui.rules_changed)
        self.ui.download.clicked.connect(self.save_rules)
        self.ui.validate.clicked.connect(self.validate_rules)

        # with open("avaya_rules.json") as f:
        #     config_data = json.load(f)

        # start = QPushButton("Start")
        # main_layout.addWidget(start)
        # start.clicked.connect(self.start_thread)

        self.val = SchemaValidator("./schemas", "/schemas/main")

    def progress_received(self, currentRuleIndex, totalRules):
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
        total_errors = 0
        rules_inputs = self.ui.stacked_widget.get_form_factories()

        if len(rules_inputs) == 0:
            return None

        for rule in rules_inputs:

            error_count, form_errors, data = rule.validate_form()

            total_errors = total_errors + error_count

            rules.append(data)

        if total_errors > 0:
            self.ui.validate_feedback.setText(f"Total Errors :{total_errors}")
            self.ui.validate_feedback.setIcon(self.ui.error_icon)
            # TODO - display notification - display errors
            return None
        else:
            self.ui.validate_feedback.setText("No Errors Found")
            self.ui.validate_feedback.setIcon(self.ui.no_error_icon)
            [rule.pop("errors", None) for rule in rules]
            data = {"rules": rules}
            return data

    def save_rules(self):
        data = self.validate_rules()
        if data:
            with open("./avaya_user.json", "w") as f:
                json.dump(data, f, indent=4)
            # TODO Confirmation message - toast
