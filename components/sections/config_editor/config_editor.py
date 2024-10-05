import json
import os

from PySide6.QtWidgets import QVBoxLayout, QWidget

from models import RulesModel
from services.validator import ValidationError

from .config_editor_view import ConfigEditorView


class ConfigEditor(QWidget):
    def __init__(self, config):
        super().__init__()
        self.setObjectName("config-editor")
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "config_editor.css")

        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.config = config
        self.current_rule_index = 0

        main_layout = QVBoxLayout(self)
        self.ui = ConfigEditorView(self.config)
        main_layout.addWidget(self.ui)
        self.rulesModel = RulesModel()

        self.rulesModel.data_changed.connect(self.ui.rules_changed)

        self.ui.save_button.clicked.connect(self.save_config)

    def save_config(self):
        rules = []
        total_errors = 0
        for rule in self.ui.stacked_widget.get_form_factories():

            error_count, form_errors, data = rule.validate_form()

            total_errors = total_errors + error_count

            rules.append(data)

        if total_errors > 0:
            self.ui.validate_feedback.setText(f"Total Errors :{total_errors}")
            # TODO - display notification - display errors
        else:
            self.ui.validate_feedback.setText("No Errors Found")
            [rule.pop("errors", None) for rule in rules]
            data = {"rules": rules}
            with open("./avaya_user.json", "w") as f:
                json.dump(data, f, indent=4)
            # TODO Confirmation message - toast

    def highlight_errors(self, rule):
        def set_sheet(el, status=False):
            if status:
                color = "green"
            else:
                color = "red"
            el.setStyleSheet(f"border: 1px solid {color};")

        def turn_green(field_refs):
            if isinstance(field_refs, ValidationError):
                return

            for field in field_refs.values():
                if isinstance(field, dict):
                    turn_green(field)
                elif isinstance(field, list):
                    for list_item in field:
                        turn_green(list_item)
                else:
                    set_sheet(field, status=True)

        turn_green(rule)

        def get_value_from_path(data, path):
            current = data
            for key in path:
                try:
                    current = current[key]
                except Exception as e:
                    print(e)
            return current

        for error in rule["errors"]:
            path = error.path
            element = get_value_from_path(rule, path)
            if element is not None:
                set_sheet(element)
