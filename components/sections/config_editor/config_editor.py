import json

from PySide6.QtWidgets import QLineEdit, QTextEdit, QVBoxLayout, QWidget

from services.validator import SchemaValidator, ValidationError

from .config_editor_view import ConfigEditorView


class ConfigEditor(QWidget):
    def __init__(self, config):
        super().__init__()
        self.setObjectName("config-editor")

        self.config = config
        self.current_rule_index = 0

        main_layout = QVBoxLayout(self)
        self.ui = ConfigEditorView(self.config)
        main_layout.addWidget(self.ui)

        self.ui.save_button.clicked.connect(self.save_config)

    def make_rule_dict(self, field_refs, int_keys):
        x = {}
        if isinstance(field_refs, ValidationError):
            return
        for key, field in field_refs.items():
            if isinstance(field, dict):
                x[key] = self.make_rule_dict(field, int_keys)
            elif isinstance(field, list):
                x[key] = [self.make_rule_dict(item, int_keys) for item in field]
            else:
                if key in int_keys:
                    if field.text().isdigit():
                        x[key] = int(field.text())
                elif isinstance(field, QLineEdit):
                    x[key] = field.text()
                elif isinstance(field, QTextEdit):
                    x[key] = field.toPlainText()
        return x

    def save_config(self):
        rules = []
        val = SchemaValidator("./schemas", "/schemas/rules")
        total_errors = 0
        for rule in self.ui.rules_inputs:

            dat_rule = self.make_rule_dict(
                rule, ("time_interval", "equality_threshold")
            )

            validate = val.get_validator()
            rule["errors"] = []
            for error in validate.iter_errors(dat_rule):
                rule["errors"].append(error)
                total_errors = total_errors + 1

            self.highlight_errors(rule)

            rules.append(dat_rule)
        if total_errors > 0:
            self.ui.validate_feedback.setText(f"Total Errors :{total_errors}")
        else:
            self.ui.validate_feedback.setText("No Errors Found")
        data = {"rules": rules}
        with open("./avaya_user.json", "w") as f:
            json.dump(data, f, indent=4)

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
