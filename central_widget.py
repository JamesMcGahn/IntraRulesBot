import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from configeditor import ConfigEditor
from keys import keys
from rule_runner_thread import RuleRunnerThread


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        with open("avaya_rules.json") as f:
            config_data = json.load(f)
        self.config_editor = ConfigEditor(config_data)
        main_layout.addWidget(self.config_editor)

        start = QPushButton("start thread")
        main_layout.addWidget(start)
        start.clicked.connect(self.start_thread)

    def start_thread(self):
        config_data = None
        with open("avaya_rules.json") as f:
            config_data = json.load(f)
        self.thread = RuleRunnerThread(
            keys["login"], keys["password"], keys["url"], config_data["rules"]
        )
        self.thread.start()
