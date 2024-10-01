from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFormLayout,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.helpers import WidgetFactory
from components.layouts import ScrollArea, StackedWidget
from services.validator import ValidationError


class ConfigEditorView(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.current_rule_index = 0
        self.rules_inputs = []
        self.rules = []
        self.init_ui()

    def init_ui(self):
        self.setObjectName("Config-Editor-View")

        self.current_rule_index = 0
        self.main_layout = QVBoxLayout(self)

        self.stacked_widget = StackedWidget()
        self.stacked_widget.setObjectName("Rules-Stacked-Widget")
        self.stacked_widget.setContentsMargins(10, 10, 15, 10)
        self.no_rules_label = QLabel("Open a File or Add a Rule.")

        self.main_layout.addWidget(self.stacked_widget)
        scroll_area = ScrollArea(self)
        scroll_area.setWidget(self.stacked_widget)

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(5)
        shadow_effect.setXOffset(3)
        shadow_effect.setYOffset(3)
        shadow_effect.setColor(QColor(0, 0, 0, 60))
        scroll_area.setGraphicsEffect(shadow_effect)

        self.set_up_rules()

        nav_btn_layout = QHBoxLayout()
        self.nav_label = QLabel()
        self.nav_label.setStyleSheet("background: transparent;")
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.clicked.connect(self.show_previous_rule)
        self.next_button.clicked.connect(self.show_next_rule)
        nav_btn_layout.addWidget(self.nav_label)
        nav_btn_layout.addWidget(self.prev_button)
        nav_btn_layout.addWidget(self.next_button)

        bottom_btn_layout = QHBoxLayout()
        self.validate_feedback = QPushButton()
        self.validate_feedback.setStyleSheet(
            "background-color: transparent; border: none;"
        )
        self.save_button = QPushButton("Save to File")
        self.validate_button = QPushButton("Validate")
        bottom_btn_layout.addWidget(self.validate_feedback)
        bottom_btn_layout.addWidget(self.save_button)
        bottom_btn_layout.addWidget(self.validate_button)

        self.main_layout.addLayout(nav_btn_layout)
        self.main_layout.addWidget(scroll_area)
        self.main_layout.addLayout(bottom_btn_layout)
        self.update_navigation_buttons()

    def set_up_rules(self):
        if self.rules:
            self.stacked_widget.remove_by_name("No-Rules-Widget")
            self.no_rules_label.setHidden(True)
            for rule in self.rules:
                self.create_rule_form(rule)
            self.update_navigation_buttons()
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {len(self.rules_inputs)}"
            )
        else:
            self.stacked_widget.add_widget("No-Rules-Widget", self.no_rules_label)

    @Slot(list)
    def rules_changed(self, rules):
        print(rules)
        self.rules = rules
        self.set_up_rules()

    def update_navigation_buttons(self):
        self.prev_button.setDisabled(self.current_rule_index == 0)
        self.next_button.setDisabled(
            self.current_rule_index >= len(self.rules_inputs) - 1
        )

    def show_previous_rule(self):
        if self.current_rule_index > 0:
            self.current_rule_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {self.stacked_widget.count()}"
            )
        self.update_navigation_buttons()

    def show_next_rule(self):
        if self.current_rule_index < self.stacked_widget.count() - 1:
            self.current_rule_index += 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {self.stacked_widget.count()}"
            )
            self.prev_button.setDisabled(False)
        self.update_navigation_buttons()

    def create_text_input_row(
        self,
        line_edit_value: str,
        label_text: str,
        parent_layout: QFormLayout,
        rule_input: dict = None,
        rule_input_path: str = None,
    ):

        el = WidgetFactory.create_form_input_row(
            line_edit_value, label_text, parent_layout
        )

        if rule_input_path is not None and rule_input is not None:
            rule_input[rule_input_path] = el
        return el

    def rf_add_general_settings(self, rule, rule_input, rule_layout):
        general_settings_layout = WidgetFactory.create_form_box(
            "General Settings",
            rule_layout,
            [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
            "#f58321",
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
                "#f58321",
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

    # TODO Refactor
    def rf_add_conditions_settings(self, rule, rule_input, rule_layout):
        rule_input["conditions"] = []
        for i, condition in enumerate(rule["conditions"]):
            title = condition["details"]["condition_type"].title()

            condition_layout = WidgetFactory.create_form_box(
                f"Condition - {(i+1)} - {title}",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58321",
            )
            inputs = self.create_condition_fields(condition_layout, condition)
            rule_input["conditions"].append(inputs)

    # TODO Refactor
    def rf_add_actions_settings(self, rule, rule_input, rule_layout):
        rule_input["actions"] = []
        for i, action in enumerate(rule["actions"]):
            title = action["details"]["action_type"].title()

            action_layout = WidgetFactory.create_form_box(
                f"Action - {(i+1)} - {title}",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58321",
            )

            inputs = self.create_action_fields(action_layout, action)
            rule_input["actions"].append(inputs)

    def create_rule_form(self, rule):
        rule_input = {}
        rules_name = rule["rule_name"]
        rules_guid = rule["guid"]
        rule_widget = QWidget()
        rule_input["guid"] = rules_guid
        rule_outter_layout = QFormLayout()

        rule_layout = WidgetFactory.create_form_box(
            f"Rule Configuration - {rules_name}",
            rule_outter_layout,
            False,
            object_name="Rules-Container",
        )
        rule_widget.setLayout(rule_outter_layout)

        self.rf_add_general_settings(rule, rule_input, rule_layout)
        self.rf_add_trigger_settings(rule, rule_input, rule_layout)
        self.rf_add_conditions_settings(rule, rule_input, rule_layout)
        self.rf_add_actions_settings(rule, rule_input, rule_layout)

        self.stacked_widget.add_widget(rules_guid, rule_widget)
        self.rules_inputs.append(rule_input.copy())

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

    def create_condition_fields(self, parent_layout, condition):
        # Common fields
        condition_data = {}

        condition_general_settings_layout = WidgetFactory.create_form_box(
            "Condition Provider Settings",
            parent_layout,
            False,
            object_name="Condition-Provider",
            drop_shadow_effect=False,
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
