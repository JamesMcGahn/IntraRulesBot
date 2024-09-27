import json

from jsonschema import ValidationError
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from components.sections import ConfigEditor
from keys import keys
from rulerunner import RuleRunnerThread
from services.logger import Logger
from services.validator import SchemaValidator


class HeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)

        with open("avaya_rules.json") as f:
            config_data = json.load(f)

        self.open_btn = QPushButton("Open File")

        main_layout.addWidget(self.open_btn)
        self.open_btn.clicked.connect(self.open_json_file)

        self.val = SchemaValidator("./schemas", "/schemas/main")

    def open_json_file(self):
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
                    # self.display_data(data)
                self.val.validate(data)
                # validate(instance=data, schema=self.main_schema, res)
            except ValidationError as e:
                print(e)
                # print(e.json_path)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Theres an error with your file: \n {e.message} \n {e.instance} \n",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load JSON file: {e}")
