from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule
    from .fields.rule_field_factory import RuleFieldFactory

from PySide6.QtWidgets import QFormLayout, QLineEdit

from views.components.helpers.widget_factory import WidgetFactory

from .rule_widget import RuleWidget
from .builders.general_settings_builder import GeneralSettingsBuilder
from .builders.trigger_builder import TriggerBuilder
from .builders.conditions_builder import ConditionsBuilder
from .builders.actions_builder import ActionsBuilder


class RuleFactory:

    def __init__(
        self,
        field_factory: RuleFieldFactory,
        general_builder: GeneralSettingsBuilder,
        trigger_builder: TriggerBuilder,
        condition_builder: ConditionsBuilder,
        action_builder: ActionsBuilder,
    ):
        self._general_builder = general_builder
        self._trigger_builder = trigger_builder
        self._condition_builder = condition_builder
        self._action_builder = action_builder
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
        self._action_builder.build(rule_layout)

        return rule_outter_layout
