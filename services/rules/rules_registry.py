from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Rule
    from services.logger.adapters import LogAdapter

from base import ServiceBase


class RuleRegistry(ServiceBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger)
        self.rules: dict[str, Rule] = {}

    def upsert(self, rule: Rule):
        self.rules[rule.guid] = rule

    def add_rules(self, rules: list[Rule]):
        for rule in rules:
            self.upsert(rule)

    def delete(self, rule_guid: str) -> str | None:
        return self.rules.pop(rule_guid, None)

    def delete_all(self):
        self.rules.clear()

    def get(self, guid: str) -> Rule | None:
        return self.rules.get(guid)

    def get_all(self) -> list[Rule]:
        return list(self.rules.values())
