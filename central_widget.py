import json

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from components.sections import ConfigEditor, HeaderWidget
from keys import keys
from rulerunner import RuleRunnerThread
from services.validator import SchemaValidator


class CentralWidget(QWidget):
    appshutdown = Signal()
    send_logs = Signal(str, str, bool)

    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)

        with open("avaya_rules.json") as f:
            config_data = json.load(f)

        self.config_editor = ConfigEditor(config_data)
        self.header_widget = HeaderWidget()

        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.config_editor)

        start = QPushButton("Start")
        main_layout.addWidget(start)
        start.clicked.connect(self.start_thread)

        self.val = SchemaValidator("./schemas", "/schemas/main")

    @Slot()
    def notified_app_shutting(
        self,
    ):
        self.appshutdown.emit()

    def start_thread(self):
        config_data = None
        with open("avaya_rules.json") as f:
            config_data = json.load(f)

        self.rule_runner_thread = RuleRunnerThread(
            keys["login"], keys["password"], keys["url"], config_data["rules"]
        )
        self.rule_runner_thread.send_insert_logs.connect(self.send_logs)
        self.appshutdown.connect(self.rule_runner_thread.close)
        self.rule_runner_thread.start()
