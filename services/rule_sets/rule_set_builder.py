from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..rules.rule_builder import RuleBuilder
from .models import RuleSet

from uuid import uuid4


class RuleSetBuilder:

    def __init__(self, rule_builder: RuleBuilder):
        super().__init__()
        self.rule_builder = rule_builder

    def build_rule_set(self, rule_set: dict) -> RuleSet:
        rule_set_name = rule_set.get("rule_set_name", "Rule Set Has No Name")
        rule_set_description = rule_set.get("description", "")
        rules = rule_set.get("rules", [])
        guid = rule_set.get("guid", str(uuid4()))
        default = rule_set.get("default", False)
        built_rules = self.rule_builder.build_rules(rules)
        return RuleSet(
            rule_set_name=rule_set_name,
            guid=guid,
            description=rule_set_description,
            rules=built_rules,
            default=default,
        )

    def build_rule_sets(self, rule_sets: list[dict]) -> list[RuleSet]:
        return [self.build_rule_set(rule) for rule in rule_sets]
