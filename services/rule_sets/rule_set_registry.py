from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import RuleSet
    from services.logger.adapters import LogAdapter

from base import ServiceBase


class RuleSetRegistry(ServiceBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger)
        self.rule_sets: dict[str, RuleSet] = {}

    def upsert(self, rule_set: RuleSet):
        self.rule_sets[rule_set.guid] = rule_set

    def add_rule_sets(self, rule_sets: list[RuleSet]):
        for rule_set in rule_sets:
            self.upsert(rule_set)

    def delete(self, rule_set_guid: str) -> list[str]:
        rule_set = self.rule_sets.get(rule_set_guid)
        if rule_set is None or rule_set.default:
            return None

        return self.rule_sets.pop(rule_set_guid)

    def clear_user_rulesets(self):
        guids_to_delete = [
            guid for guid, rule_set in self.rule_sets.items() if not rule_set.default
        ]
        for guid in guids_to_delete:
            self.rule_sets.pop(guid)

    def get(self, guid: str) -> RuleSet | None:
        return self.rule_sets.get(guid)

    def get_all(self):
        return [rule_set for rule_set in self.rule_sets.values()]

    def get_all_user_rulesets(self) -> list[RuleSet]:
        return [
            rule_set for rule_set in self.rule_sets.values() if not rule_set.default
        ]
