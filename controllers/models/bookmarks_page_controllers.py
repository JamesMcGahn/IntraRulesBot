from dataclasses import dataclass

from ..rule_sets.rule_sets_controller import RuleSetsController


@dataclass
class BookmarksPageControllers:
    rule_sets: RuleSetsController
