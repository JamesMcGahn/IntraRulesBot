from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Rule
    from .models import RuleSet

from base import QObjectBase
from base.enums import LOGLEVEL


class RuleRegistry(QObjectBase):

    def __init__(self):
        super().__init__()
        self.rules: dict[str, Rule] = {}
        self.rule_sets: dict[str, RuleSet] = {}

    def upsert(self, rule: Rule):
        self.rules[rule.guid] = rule

    def add_rules(self, rules: list[Rule]):
        for rule in rules:
            self.upsert(rule)

    def delete(self, rule_guid: str) -> list[str]:
        rule = self.rules.pop(rule_guid, None)
        if rule is None:
            return []
        affected_rule_sets = []
        for rules_set in self.rule_sets.values():
            if rule.guid in rules_set.rules_guids:
                rules_set.rules_guids.remove(rule.guid)
                affected_rule_sets.append(rules_set.guid)
        return affected_rule_sets

    def delete_all(self):
        self.rules.clear()
        self.rule_sets.clear()

    def get(self, guid: str) -> Rule | None:
        return self.rules.get(guid)

    def get_all(self) -> list[Rule]:
        return list(self.rules.values())

    def add_rule_set(self, rule_set: RuleSet):
        missing_rules = [
            rule_guid
            for rule_guid in rule_set.rules_guids
            if rule_guid not in self.rules
        ]
        if missing_rules:
            message = f"{rule_set.rule_set_name} contains missing rule guids: {missing_rules.join(",")}"
            self.logging(message, LOGLEVEL.ERROR)
            raise ValueError(message)
        self.rule_sets[rule_set.guid] = rule_set

    def get_rule_set(self, guid: str) -> RuleSet | None:
        return self.rule_sets.get(guid)

    def get_rules_for_set(self, rule_set_guid: str) -> list[Rule]:
        rule_set = self.get_rule_set(rule_set_guid)
        if not rule_set:
            return []
        return [
            self.rules[rule_guid]
            for rule_guid in rule_set.rules_guids
            if rule_guid in self.rules
        ]
