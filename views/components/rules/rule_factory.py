from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule

from typing import Optional

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QTextEdit

from views.components.helpers.widget_factory import WidgetFactory

from services.rules.models.triggers import FrequencyTrigger
from services.rules.models.triggers.action_based import ActionTrigger
from services.rules.models.conditions import Condition
from services.rules.models.actions import Action

from .rule_widget import RuleWidget


class RuleFactory:

    def build(self, rule: Rule, style=""):
        layout, field_map = self.create_rule_form(rule)
        widget = RuleWidget().add_inner_layout(layout, style)
        return widget, field_map

    def create_rule_form(self, rule: Rule) -> None:
        """
        Creates the form layout for the given rule.

        Args:
            rule (dict): The rule data used to generate the form layout.

        Returns:
            None: This function does not return a value.
        """
        rule_inputs = {}
        rules_name = rule.rule_name
        rule_guid = rule.guid
        self._rule_guid = rule.guid
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
        self.rf_add_action_based_settings(rule, rule_inputs, rule_layout)
        self.rf_add_conditions_settings(rule, rule_inputs, rule_layout)
        self.rf_add_actions_settings(rule, rule_inputs, rule_layout)

        return rule_outter_layout, rule_inputs

    def create_text_input_row(
        self,
        line_edit_value: str,
        label_text: str,
        parent_layout: QFormLayout,
        rule_input: Optional[dict] = None,
        rule_input_path: Optional[str] = None,
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
            rule_input_path=rule_input_path,
            guid=self._rule_guid,
        )

        if rule_input_path is not None and rule_input is not None:
            rule_input[rule_input_path] = el
        return el

    def rf_add_general_settings(
        self, rule: Rule, rule_input: dict, rule_layout: QFormLayout
    ) -> None:
        """
        Adds general settings fields to the form layout.

        Args:
            rule (dict): The rule data containing general settings.
            rule_input (dict): The input fields for the rule.
            rule_layout (QFormLayout): The layout for the form.

        Returns:
            None: This function does not return a value.
        """
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
            rule.rule_name,
            "Rule Name:",
            general_settings_layout,
            rule_input,
            "rule_name",
        )
        self.create_text_input_row(
            rule.rule_category,
            "Rule Category:",
            general_settings_layout,
            rule_input,
            "rule_category",
        )

    def rf_add_trigger_settings(
        self, rule: Rule, rule_input: dict, rule_layout: QFormLayout
    ) -> None:
        """
        Adds trigger settings fields to the form layout.

        Args:
            rule (dict): The rule data containing trigger settings.
            rule_input (dict): The input fields for the rule.
            rule_layout (QFormLayout): The layout for the form.

        Returns:
            None: This function does not return a value.
        """
        if isinstance(rule.trigger, FrequencyTrigger):
            frequency_settings_layout = WidgetFactory.create_form_box(
                "Frequency Settings",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58220",
                drop_shadow_effect=False,
                title_font_size=13,
                title_color="#fcfcfc",
            )
            freq_int = str(rule.trigger.time_interval)
            frequency_based_set = {}

            self.create_text_input_row(
                freq_int,
                "Time Interval:",
                frequency_settings_layout,
                frequency_based_set,
                "time_interval",
            )

            rule_input["frequency_based"] = frequency_based_set

    def rf_add_action_based_settings(
        self, rule: Rule, rule_input: dict, rule_layout: QFormLayout
    ) -> None:
        """
        Adds condition settings fields to the form layout.

        Args:
            rule (dict): The rule data containing condition settings.
            rule_input (dict): The input fields for the rule.
            rule_layout (QFormLayout): The layout for the form.

        Returns:
            None: This function does not return a value.
        """

        if isinstance(rule.trigger, ActionTrigger):
            action_based_settings_layout = WidgetFactory.create_form_box(
                "Action Trigger Settings",
                rule_layout,
                [(0.05, "#F2F3F2"), (0.50, "#DEDEDE"), (1, "#DEDEDE")],
                "#f58220",
                drop_shadow_effect=False,
                title_font_size=13,
                title_color="#fcfcfc",
            )

            rule_input["action_based"] = self.create_action_based_fields(
                action_based_settings_layout, rule.trigger
            )

    def rf_add_conditions_settings(
        self, rule: Rule, rule_input: dict, rule_layout: QFormLayout
    ) -> None:
        """
        Adds condition settings fields to the form layout.

        Args:
            rule (dict): The rule data containing condition settings.
            rule_input (dict): The input fields for the rule.
            rule_layout (QFormLayout): The layout for the form.

        Returns:
            None: This function does not return a value.
        """
        rule_input["conditions"] = []
        for i, condition in enumerate(rule.conditions):
            title = condition.details.condition_type.title()

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

    def rf_add_actions_settings(
        self, rule: Rule, rule_input: dict, rule_layout: QFormLayout
    ) -> None:
        """
        Adds action settings fields to the form layout.

        Args:
            rule (dict): The rule data containing action settings.
            rule_input (dict): The input fields for the rule.
            rule_layout (QFormLayout): The layout for the form.

        Returns:
            None: This function does not return a value.
        """
        rule_input["actions"] = []
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

            inputs = self.create_action_fields(action_layout, action)
            rule_input["actions"].append(inputs)

    def create_action_based_fields(
        self, parent_layout: QFormLayout, trigger: ActionTrigger
    ) -> dict:
        """
        Creates form fields for the given condition.

        Args:
            parent_layout (QFormLayout): The parent layout for the condition fields.
            condition (dict): The condition data used to generate the form fields.

        Returns:
            dict: A dictionary of form fields for the condition.
        """
        # Common fields
        action_based_data = {}

        action_based_general_settings_layout = WidgetFactory.create_form_box(
            "Action Trigger Provider Settings",
            parent_layout,
            False,
            object_name="Action-Based-Provider",
            drop_shadow_effect=False,
            title_font_size=11,
        )

        action_based_fields = [
            (
                trigger.provider_category,
                "Provider Category:",
                "provider_category",
            ),
            (
                trigger.provider_instance,
                "Provider Instance:",
                "provider_instance",
            ),
            (
                trigger.provider_condition,
                "Provider Condition:",
                "provider_condition",
            ),
        ]

        for initial_value, label_text, rule_input_path in action_based_fields:
            self.create_text_input_row(
                initial_value,
                label_text,
                action_based_general_settings_layout,
                action_based_data,
                rule_input_path,
            )

        details_data = {}

        # Check details for condition type
        details = trigger.details
        if details.action_type == "state_changed":
            title = trigger.provider_condition
            details_layout = WidgetFactory.create_form_box(
                f"{title} Settings",
                parent_layout,
                False,
                object_name="Action-Trigger-Details-State",
                drop_shadow_effect=False,
                title_font_size=11,
            )
            state_layout = WidgetFactory.create_form_box(
                "State",
                details_layout,
                False,
                object_name="Action-Trigger-State",
                drop_shadow_effect=False,
                title_font_size=11,
            )

            state_data = []
            for state in details.state:
                state_obj = {}
                self.create_text_input_row(
                    state.state, "State", state_layout, state_obj, "state"
                )
                self.create_text_input_row(
                    state.aux, "Aux", state_layout, state_obj, "aux"
                )
                state_data.append(state_obj)

            detail_fields = [
                (
                    details.action_type,
                    "Action Type:",
                    "action_type",
                ),
                (
                    details.equality_operator,
                    "Equality Operator:",
                    "equality_operator",
                ),
                (
                    details.user_list,
                    "User List:",
                    "user_list",
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

        action_based_data["details"] = details_data
        action_based_data["details"]["state"] = state_data
        return action_based_data

    def create_condition_fields(
        self, parent_layout: QFormLayout, condition: Condition
    ) -> dict:
        """
        Creates form fields for the given condition.

        Args:
            parent_layout (QFormLayout): The parent layout for the condition fields.
            condition (dict): The condition data used to generate the form fields.

        Returns:
            dict: A dictionary of form fields for the condition.
        """
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
                condition.provider_category,
                "Provider Category:",
                "provider_category",
            ),
            (
                condition.provider_instance,
                "Provider Instance:",
                "provider_instance",
            ),
            (
                condition.provider_condition,
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
        details = condition.details
        if details.condition_type == "stats":
            title = condition.provider_condition
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
                    details.condition_type,
                    "Condition Type:",
                    "condition_type",
                ),
                (
                    details.equality_operator,
                    "Equality Operator:",
                    "equality_operator",
                ),
                (
                    str(details.equality_threshold),
                    "Equality Threshold:",
                    "equality_threshold",
                ),
                (
                    details.queues_source,
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

    def create_action_fields(self, parent_layout: QFormLayout, action: Action) -> dict:
        """
        Creates form fields for the given action.

        Args:
            parent_layout (QFormLayout): The parent layout for the action fields.
            action (dict): The action data used to generate the form fields.

        Returns:
            dict: A dictionary of form fields for the action.
        """
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
            (action.provider_category, "Provider Category:", "provider_category"),
            (action.provider_instance, "Provider Instance:", "provider_instance"),
            (action.provider_condition, "Provider Instance:", "provider_condition"),
        ]
        for initial_value, label_text, rule_input_path in action_fields:
            self.create_text_input_row(
                initial_value,
                label_text,
                action_general_settings_layout,
                action_data,
                rule_input_path,
            )

        details = action.details
        details_data = {}

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
                self.create_text_input_row(
                    initial_value,
                    label_text,
                    details_layout,
                    details_data,
                    rule_input_path,
                )

            email_body_input = QTextEdit(str(details.email_body))
            email_body_label = QLabel("Email Body:")
            email_body_label.setStyleSheet("background-color: transparent")
            email_body_input.setStyleSheet("background-color: #FCFCFC")
            details_layout.addRow(email_body_label, email_body_input)
            details_data["email_body"] = email_body_input

        action_data["details"] = details_data
        return action_data
