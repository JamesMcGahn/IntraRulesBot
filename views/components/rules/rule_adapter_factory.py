from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fields.rule_registry import RuleFieldRegistry
    from .rule_event_filter import RuleEventFilter
    from services.rules.models import Rule
from .fields.rule_registry import RuleFieldRegistry
from .rule_factory import RuleFactory
from .rule_adapter import RuleAdapter
from .field_converters import FIELD_CONVERTERS
from .fields.rule_field_factory import RuleFieldFactory
from .builders.general_settings_builder import GeneralSettingsBuilder
from .builders.trigger_builder import TriggerBuilder
from .builders.action_trigger_details_builder import ActionTriggerDetailsBuilder
from .builders.conditions_builder import ConditionsBuilder


class RuleAdapterFactory:

    def __init__(self, event_filter: RuleEventFilter):
        self.event_filter = event_filter

    def build(self, rule: Rule):
        registry = RuleFieldRegistry()
        field_factory = RuleFieldFactory(registry, self.event_filter)
        field_factory.rule_guid = rule.guid

        general_builder = GeneralSettingsBuilder(field_factory, rule)
        trigger_details_builder = ActionTriggerDetailsBuilder(field_factory, rule)
        trigger_builder = TriggerBuilder(field_factory, rule, trigger_details_builder)
        condition_builder = ConditionsBuilder(field_factory, rule)
        widget = RuleFactory(
            field_factory, general_builder, trigger_builder, condition_builder
        ).build(rule, "margin-top: 0px; padding-left: 0px;padding-top: 0px;")
        return RuleAdapter(
            guid=rule.guid,
            widget=widget,
            field_registry=registry,
            field_converters=FIELD_CONVERTERS,
        )
