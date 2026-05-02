from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.rules.models import Rule

from dataclasses import dataclass


@dataclass
class RulesLoadedEvent:
    rules: list[Rule]
