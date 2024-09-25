import json

from jsonschema import ValidationError
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from configeditor import ConfigEditor
from keys import keys
from rule_runner_thread import RuleRunnerThread
from schema_validator import SchemaValidator
from services.logger import Logger


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        with open("avaya_rules.json") as f:
            config_data = json.load(f)
        self.config_editor = ConfigEditor(config_data)

        self.user_load_label = QLabel("Open Your Own File or Load the default")
        self.load_def_btn = QPushButton("Open Default File")
        self.open_btn = QPushButton("Open JSON File")
        main_layout.addWidget(self.user_load_label)
        main_layout.addWidget(self.load_def_btn)
        main_layout.addWidget(self.open_btn)
        self.open_btn.clicked.connect(self.open_json_file)

        self.logger = Logger()

        main_layout.addWidget(self.config_editor)

        start = QPushButton("start thread")
        main_layout.addWidget(start)
        start.clicked.connect(self.start_thread)

        # with open("./schemas/main_schema.json", "r") as main_schema_file:
        #     main_schema = json.load(main_schema_file)

        # with open("./schemas/rules_schema.json", "r") as rules_schema_file:
        #     rules_schema = json.load(rules_schema_file)

        # schema_store = {
        #     main_schema["$id"]: main_schema,
        #     rules_schema["$id"]: rules_schema,
        # }
        # resolver = RefResolver.from_schema(main_schema, store=schema_store)
        # self.validator = Draft202012Validator(main_schema, resolver=resolver)

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
                print(e.json_path)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Theres an error with your file: \n {e.message} \n {e.instance} \n",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load JSON file: {e}")

    def start_thread(self):
        config_data = None
        with open("avaya_rules.json") as f:
            config_data = json.load(f)

        self.rule_runner_thread = RuleRunnerThread(
            keys["login"], keys["password"], keys["url"], config_data["rules"]
        )
        self.rule_runner_thread.send_insert_logs.connect(self.logger.insert)
        self.rule_runner_thread.start()
