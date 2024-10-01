import json

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from components.sections import ConfigEditor
from keys import keys
from rulerunner import RuleRunnerThread
from services.validator import SchemaValidator


class RulesPage(QWidget):
    appshutdown = Signal()
    send_logs = Signal(str, str, bool)

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)

        self.setAttribute(Qt.WA_StyledBackground, True)

        with open("avaya_rules.json") as f:
            config_data = json.load(f)

        self.config_editor = ConfigEditor(config_data)

        main_layout.addWidget(self.config_editor)

        start = QPushButton("Start")
        main_layout.addWidget(start)
        start.clicked.connect(self.start_thread)

        self.val = SchemaValidator("./schemas", "/schemas/main")

    @Slot(str, str, bool)
    def logging(self, msg, level="INFO", print_msg=True):
        self.send_logs.emit(msg, level, print_msg)

    @Slot()
    def notified_app_shutting(self):
        self.appshutdown.emit()

    def start_thread(self):
        config_data = None
        with open("avaya_rules.json") as f:
            config_data = json.load(f)

        self.rule_runner_thread = RuleRunnerThread(
            keys["login"], keys["password"], keys["url"], config_data["rules"]
        )
        self.rule_runner_thread.send_insert_logs.connect(self.logging)
        self.appshutdown.connect(self.rule_runner_thread.close)
        self.rule_runner_thread.start()
