from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fields.rule_registry import RuleFieldRegistry
    from .rule_event_filter import RuleEventFilter
    from services.rules.models import Rule
from .rule_registry import RuleFieldRegistry
from .rule_factory import RuleFactory
from .rule_adapter import RuleAdapter
from .field_converters import FIELD_CONVERTERS


class RuleAdapterFactory:

    def __init__(self, event_filter: RuleEventFilter):
        self.event_filter = event_filter

    def build(self, rule: Rule):
        registry = RuleFieldRegistry()
        widget = RuleFactory(registry, self.event_filter).build(
            rule, "margin-top: 0px; padding-left: 0px;padding-top: 0px;"
        )
        return RuleAdapter(
            guid=rule.guid,
            widget=widget,
            field_registry=registry,
            field_converters=FIELD_CONVERTERS,
        )
