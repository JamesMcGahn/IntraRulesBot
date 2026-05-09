from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..rules.models import Rule

from ..rules.models.triggers import ActionTrigger, FrequencyTrigger

from dataclasses import asdict
from enum import Enum


class RuleSerializer:

    def to_schema_dict(self, rule: Rule) -> dict:
        schema_dict = {
            "guid": rule.guid,
            "rule_name": rule.rule_name,
            "rule_category": rule.rule_category,
            "conditions": [
                self.normalize(asdict(condition)) for condition in rule.conditions
            ],
            "actions": [self.normalize(asdict(action)) for action in rule.actions],
        }

        if isinstance(rule.trigger, FrequencyTrigger):
            schema_dict["frequency_based"] = self.normalize(asdict(rule.trigger))

        elif isinstance(rule.trigger, ActionTrigger):
            schema_dict["action_based"] = self.normalize(asdict(rule.trigger))

        return schema_dict

    def normalize(self, obj):
        if isinstance(obj, Enum):
            return obj.value

        if isinstance(obj, list):
            return [self.normalize(x) for x in obj]

        if isinstance(obj, dict):
            return {k: self.normalize(v) for k, v in obj.items()}

        return obj
