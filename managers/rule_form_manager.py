from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QTextEdit

from components.helpers.widget_factory import WidgetFactory
from services.validator import SchemaValidator, ValidationError


class RuleFormManager:
    def __init__(
        self,
        rule,
        schema_folder="./schemas",
        schema_path="/schemas/rules",
        int_keys=("time_interval", "equality_threshold"),
    ):
        super().__init__()
        self.rule = rule

        self._rule_form = None
        self._rule_guid = None
        self._rule_inputs = None

        self.form_errors = []
        self.schema_folder = schema_folder
        self.schema_path = schema_path
        self.int_keys = int_keys
        self.create_rule_form(self.rule)

    @property
    def rule_guid(self):
        return self._rule_guid

    @property
    def rule_inputs(self):
        return self._rule_inputs

    @property
    def rule_form(self):
        return self._rule_form

    def create_rule_form(self, rule):
        rule_inputs = {}
        rules_name = rule["rule_name"]
        rule_guid = rule["guid"]
        self._rule_guid = rule["guid"]
        rule_inputs["guid"] = QLineEdit(rule_guid)
        rule_outter_layout = QFormLayout()

        rule_layout = WidgetFactory.create_form_box(
            f"Rule Configuration - {rules_name}",
            rule_outter_layout,
            False,
            object_name="Rules-Container",
            drop_shadow_effect=False,
            title_font_size=16,
            title_color="#fcfcfc",
        )
        rule_layout.setContentsMargins(12, 25, 12, 5)

        self.rf_add_general_settings(rule, rule_inputs, rule_layout)
        self.rf_add_trigger_settings(rule, rule_inputs, rule_layout)
        self.rf_add_conditions_settings(rule, rule_inputs, rule_layout)
        self.rf_add_actions_settings(rule, rule_inputs, rule_layout)

        self._rule_form = rule_outter_layout
        self._rule_guid = rule_guid
        self._rule_inputs = rule_inputs

    def create_text_input_row(
        self,
        line_edit_value: str,
        label_text: str,
        parent_layout: QFormLayout,
        rule_input: dict = None,
        rule_input_path: str = None,
    ):

        el = WidgetFactory.create_form_input_row(
            line_edit_value,
            label_text,
            parent_layout,
            rule_input_path=rule_input_path,
            guid=self._rule_guid,
        )

        if rule_input_path is not None and rule_input is not None:
            rule_input[rule_input_path] = el
        return el

    def rf_add_general_settings(self, rule, rule_input, rule_layout):
        general_settings_layout = WidgetFactory.create_form_box(
            "General Settings",
            rule_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58220",
            drop_shadow_effect=False,
            title_font_size=13,
            title_color="#fcfcfc",
        )

        self.create_text_input_row(
            rule["rule_name"],
            "Rule Name:",
            general_settings_layout,
            rule_input,
            "rule_name",
        )
        self.create_text_input_row(
            rule["rule_category"],
            "Rule Category:",
            general_settings_layout,
            rule_input,
            "rule_category",
        )

    def rf_add_trigger_settings(self, rule, rule_input, rule_layout):
        if "frequency_based" in rule:
            frequency_settings_layout = WidgetFactory.create_form_box(
                "Frequency Settings",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58220",
                drop_shadow_effect=False,
                title_font_size=13,
                title_color="#fcfcfc",
            )
            freq_int = str(rule["frequency_based"]["time_interval"])
            frequency_based_set = {}

            self.create_text_input_row(
                freq_int,
                "Time Interval:",
                frequency_settings_layout,
                frequency_based_set,
                "time_interval",
            )

            rule_input["frequency_based"] = frequency_based_set

    def rf_add_conditions_settings(self, rule, rule_input, rule_layout):
        rule_input["conditions"] = []
        for i, condition in enumerate(rule["conditions"]):
            title = condition["details"]["condition_type"].title()

            condition_layout = WidgetFactory.create_form_box(
                f"Condition - {(i+1)} - {title}",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58220",
                drop_shadow_effect=False,
                title_font_size=13,
                title_color="#fcfcfc",
            )
            inputs = self.create_condition_fields(condition_layout, condition)
            rule_input["conditions"].append(inputs)

    def rf_add_actions_settings(self, rule, rule_input, rule_layout):
        rule_input["actions"] = []
        for i, action in enumerate(rule["actions"]):
            title = action["details"]["action_type"].title()

            action_layout = WidgetFactory.create_form_box(
                f"Action - {(i+1)} - {title}",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58220",
                drop_shadow_effect=False,
                title_font_size=13,
                title_color="#fcfcfc",
            )

            inputs = self.create_action_fields(action_layout, action)
            rule_input["actions"].append(inputs)

    def validate_form(self):
        val = SchemaValidator(self.schema_path)
        total_errors = 0
        self.form_errors = []
        data_rule = self.create_input_dict(self.int_keys)
        validate = val.get_validator()
        for error in validate.iter_errors(data_rule):
            self.form_errors.append(error)
            total_errors = total_errors + 1

        self.highlight_errors(self._rule_inputs)

        return (total_errors, self.form_errors, data_rule)

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

            for key, field in field_refs.items():
                if key == "guid":
                    continue
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

        for error in self.form_errors:
            path = error.path
            element = get_value_from_path(rule, path)
            if element is not None:
                set_sheet(element)

    def create_condition_fields(self, parent_layout, condition):
        # Common fields
        condition_data = {}

        condition_general_settings_layout = WidgetFactory.create_form_box(
            "Condition Provider Settings",
            parent_layout,
            False,
            object_name="Condition-Provider",
            drop_shadow_effect=False,
            title_font_size=11,
        )

        condition_fields = [
            (
                condition["provider_category"],
                "Provider Category:",
                "provider_category",
            ),
            (
                condition["provider_instance"],
                "Provider Instance:",
                "provider_instance",
            ),
            (
                condition["provider_condition"],
                "Provider Condition:",
                "provider_condition",
            ),
        ]

        for initial_value, label_text, rule_input_path in condition_fields:
            self.create_text_input_row(
                initial_value,
                label_text,
                condition_general_settings_layout,
                condition_data,
                rule_input_path,
            )

        details_data = {}

        # Check details for condition type
        details = condition["details"]
        if details["condition_type"] == "stats":
            title = condition["provider_condition"]
            details_layout = WidgetFactory.create_form_box(
                f"{title} Settings",
                parent_layout,
                False,
                object_name="Condition-Stats",
                drop_shadow_effect=False,
                title_font_size=11,
            )

            detail_fields = [
                (
                    details["condition_type"],
                    "Condition Type:",
                    "condition_type",
                ),
                (
                    details["equality_operator"],
                    "Equality Operator:",
                    "equality_operator",
                ),
                (
                    str(details["equality_threshold"]),
                    "Equality Threshold:",
                    "equality_threshold",
                ),
                (
                    details["queues_source"],
                    "Queue Source:",
                    "queues_source",
                ),
            ]

            for initial_value, label_text, rule_input_path in detail_fields:
                self.create_text_input_row(
                    initial_value,
                    label_text,
                    details_layout,
                    details_data,
                    rule_input_path,
                )

        condition_data["details"] = details_data
        return condition_data

    def create_action_fields(self, parent_layout, action):
        action_data = {}
        action_general_settings_layout = WidgetFactory.create_form_box(
            "Action Provider Settings",
            parent_layout,
            False,
            object_name="Action-Provider",
            drop_shadow_effect=False,
            title_font_size=11,
        )

        action_fields = [
            (action["provider_category"], "Provider Category:", "provider_category"),
            (action["provider_instance"], "Provider Instance:", "provider_instance"),
            (action["provider_condition"], "Provider Instance:", "provider_condition"),
        ]
        for initial_value, label_text, rule_input_path in action_fields:
            self.create_text_input_row(
                initial_value,
                label_text,
                action_general_settings_layout,
                action_data,
                rule_input_path,
            )

        details = action["details"]
        details_data = {}

        if details["action_type"] == "email":
            title = action["provider_condition"]
            details_layout = WidgetFactory.create_form_box(
                f"{title} Settings",
                parent_layout,
                False,
                object_name="Action-Email",
                drop_shadow_effect=False,
                title_font_size=11,
            )
            detail_fields = [
                (details["action_type"], "Action Type:", "action_type"),
                (details["email_subject"], "Email Subject:", "email_subject"),
                (details["email_address"], "To Email Address:", "email_address"),
            ]

            for initial_value, label_text, rule_input_path in detail_fields:
                self.create_text_input_row(
                    initial_value,
                    label_text,
                    details_layout,
                    details_data,
                    rule_input_path,
                )

            email_body_input = QTextEdit(str(details["email_body"]))
            email_body_label = QLabel("Email Body:")
            email_body_label.setStyleSheet("background-color: transparent")
            email_body_input.setStyleSheet("background-color: #FCFCFC")
            details_layout.addRow(email_body_label, email_body_input)
            details_data["email_body"] = email_body_input

        action_data["details"] = details_data
        return action_data

    def create_input_dict(self, int_keys=("time_interval", "equality_threshold")):
        def make_rule_dict(field_refs, int_keys):
            x = {}
            if isinstance(field_refs, ValidationError):
                return
            for key, field in field_refs.items():
                if isinstance(field, dict):
                    x[key] = make_rule_dict(field, int_keys)
                elif isinstance(field, list):
                    x[key] = [make_rule_dict(item, int_keys) for item in field]
                else:
                    if key in int_keys:
                        if field.text().isdigit():
                            x[key] = int(field.text())
                        else:
                            x[key] = field.text()
                    elif isinstance(field, QLineEdit):
                        x[key] = field.text()
                    elif isinstance(field, QTextEdit):
                        x[key] = field.toPlainText()
            return x

        return make_rule_dict(self.rule_inputs, int_keys)
