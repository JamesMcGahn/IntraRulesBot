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


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        with open("avaya_rules.json") as f:
            config_data = json.load(f)
        self.config_editor = ConfigEditor(config_data)
        main_layout.addWidget(self.config_editor)
