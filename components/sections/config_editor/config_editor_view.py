from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from components.layouts import ScrollArea, StackedFormWidget
from managers import RuleFormManager
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

        self.stacked_widget = StackedFormWidget()
        self.stacked_widget.setObjectName("Rules-Stacked-Widget")
        self.stacked_widget.setContentsMargins(10, 10, 15, 10)
        self.no_rules_label = QLabel("Open a File or Add a Rule.")

        self.main_layout.addWidget(self.stacked_widget)
        scroll_area = ScrollArea(self)
        scroll_area.setWidget(self.stacked_widget)

        # TODO: call UI dropshadow helper
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

            for rule in self.rules:
                rule_form = RuleFormManager(rule)
                self.stacked_widget.add_form(rule_form)

            self.update_navigation_buttons()
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {self.stacked_widget.count()}"
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
            self.current_rule_index >= self.stacked_widget.count() - 1
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

        print("here")
        if self.current_rule_index < self.stacked_widget.count() - 1:
            self.current_rule_index += 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)
            self.nav_label.setText(
                f"Rule: {self.current_rule_index + 1} / {self.stacked_widget.count()}"
            )
            self.prev_button.setDisabled(False)
        self.update_navigation_buttons()

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
