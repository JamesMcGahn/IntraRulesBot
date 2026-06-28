from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from .fields.rule_registry import RuleFieldRegistry
    from .rule_event_filter import RuleEventFilter
    from .fields.rule_field_factory import RuleFieldFactory
from typing import Optional

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QTextEdit
from PySide6.QtCore import Qt

from views.components.helpers.widget_factory import WidgetFactory

from services.rules.models.triggers import FrequencyTrigger
from services.rules.models.triggers.action_based import ActionTrigger
from services.rules.models.conditions import Condition
from services.rules.models.actions import Action
from services.rules.enums import (
    ACTIONDETAILTYPE,
    ACTIONTRIGGERDETAILTYPE,
    CONDITIONDETAILTYPE,
)
from .rule_widget import RuleWidget
from .builders.general_settings_builder import GeneralSettingsBuilder
from .builders.trigger_builder import TriggerBuilder
from .builders.conditions_builder import ConditionsBuilder


# TODO: Refactor to be cleaner
class RuleFactory:

    def __init__(
        self,
        field_factory: RuleFieldFactory,
        general_builder: GeneralSettingsBuilder,
        trigger_builder: TriggerBuilder,
        condition_builder: ConditionsBuilder,
    ):
        self._general_builder = general_builder
        self._trigger_builder = trigger_builder
        self._condition_builder = condition_builder
        self._field_factory = field_factory
        self._field_index = {}
        self._rule_guid = None

    def build(self, rule: Rule, style=""):
        layout = self.create_rule_form(rule)
        widget = RuleWidget().add_inner_layout(layout, style)
        return widget

    def create_rule_form(self, rule: Rule) -> None:
        """
        Creates the form layout for the given rule.

        Args:
            rule (dict): The rule data used to generate the form layout.

        Returns:
            None: This function does not return a value.
        """

        rules_name = rule.rule_name
        rule_guid = rule.guid
        self._rule_guid = rule.guid
        guid_widget = QLineEdit(rule_guid)
        rule_outter_layout = QFormLayout()

        self._field_factory.register_field(guid_widget, "guid")
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

        self._general_builder.build(rule_layout)
        self._trigger_builder.build(rule_layout)
        self._condition_builder.build(rule_layout)
        # self.rf_add_conditions_settings(rule, rule_layout)
        self.rf_add_actions_settings(rule, rule_layout)

        return rule_outter_layout

    def build_path(self, *parts) -> str:
        return ".".join(str(p) for p in parts)

    def create_text_input_row(
        self,
        line_edit_value: str,
        label_text: str,
        parent_layout: QFormLayout,
        full_path: Optional[str] = None,
    ) -> QLineEdit:
        """
        Creates a text input row in the form and optionally updates the rule input dictionary.

        Args:
            line_edit_value (str): The initial value for the QLineEdit field.
            label_text (str): The label text for the input field.
            parent_layout (QFormLayout): The parent layout to which the row will be added.
            rule_input (Optional[dict]): The rule input dictionary to update.
            rule_input_path (Optional[str]): The path in the rule input dictionary to store the field.

        Returns:
            QLineEdit: The created QLineEdit field.
        """
        el = WidgetFactory.create_form_input_row(
            line_edit_value,
            label_text,
            parent_layout,
        )

        self._field_factory.register_field(el, full_path)

        return el

    def rf_add_actions_settings(self, rule: Rule, rule_layout: QFormLayout) -> None:
        """
        Adds action settings fields to the form layout.
        """

        for i, action in enumerate(rule.actions):
            title = action.details.action_type.title()

            action_layout = WidgetFactory.create_form_box(
                f"Action - {(i+1)} - {title}",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58220",
                drop_shadow_effect=False,
                title_font_size=13,
                title_color="#fcfcfc",
            )

            self.create_action_fields(action_layout, action, i)

    def create_action_fields(
        self,
        parent_layout: QFormLayout,
        action: Action,
        action_index: int,
    ) -> None:
        """
        Creates form fields for the given action.
        """
        action_general_settings_layout = WidgetFactory.create_form_box(
            "Action Provider Settings",
            parent_layout,
            False,
            object_name="Action-Provider",
            drop_shadow_effect=False,
            title_font_size=11,
        )

        action_fields = [
            (action.provider_category, "Provider Category:", "provider_category"),
            (action.provider_instance, "Provider Instance:", "provider_instance"),
            (action.provider_condition, "Provider Instance:", "provider_condition"),
        ]
        for initial_value, label_text, rule_input_path in action_fields:
            self._field_factory.text_row(
                line_edit_value=initial_value,
                label_text=label_text,
                parent_layout=action_general_settings_layout,
                full_path=self.build_path(
                    "actions",
                    action_index,
                    rule_input_path,
                ),
            )

        details = action.details

        if details.action_type == "email":
            title = action.provider_condition
            details_layout = WidgetFactory.create_form_box(
                f"{title} Settings",
                parent_layout,
                False,
                object_name="Action-Email",
                drop_shadow_effect=False,
                title_font_size=11,
            )
            detail_fields = [
                (details.action_type, "Action Type:", "action_type"),
                (details.email_subject, "Email Subject:", "email_subject"),
                (details.email_address, "To Email Address:", "email_address"),
            ]

            for initial_value, label_text, rule_input_path in detail_fields:
                self._field_factory.text_row(
                    line_edit_value=initial_value,
                    label_text=label_text,
                    parent_layout=details_layout,
                    full_path=self.build_path(
                        "actions",
                        action_index,
                        "details",
                        rule_input_path,
                    ),
                )

            email_body_input = QTextEdit(str(details.email_body))
            email_body_label = QLabel("Email Body:")
            email_body_label.setStyleSheet("background-color: transparent")
            email_body_input.setStyleSheet("""background-color: #FCFCFC;
                            color: black;
                            border-radius:3px;
                            font-size: 1em;
                            padding 8px;
                            padding-left: 10px;
                            """)
            details_layout.addRow(email_body_label, email_body_input)

            self._field_factory.register_field(
                email_body_input,
                self.build_path(
                    "actions",
                    action_index,
                    "details",
                    "email_body",
                ),
            )
