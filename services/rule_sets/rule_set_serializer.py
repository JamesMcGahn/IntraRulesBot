from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..rule_sets.models import RuleSet
    from ..rules.rule_serializer import RuleSerializer


class RuleSetSerializer:

    def __init__(self, rule_serializer: RuleSerializer):
        self.rule_serializer = rule_serializer

    def to_schema_dict(self, rule_set: RuleSet) -> dict:
        return {
            "rule_set_name": rule_set.rule_set_name,
            "description": rule_set.description,
            "guid": rule_set.guid,
            "rules": [
                self.rule_serializer.to_schema_dict(rule) for rule in rule_set.rules
            ],
        }
