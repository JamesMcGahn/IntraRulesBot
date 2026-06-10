from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rule_sets.models import RuleSet

from dataclasses import dataclass


@dataclass
class RuleSetsLoadedEvent:
    rule_sets: list[RuleSet]
