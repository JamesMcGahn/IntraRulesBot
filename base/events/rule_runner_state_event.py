from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...services.rule_runner.enums import RULERUNNERLIFECYLE

from dataclasses import dataclass


@dataclass
class RuleRunnerStateEvent:
    state: RULERUNNERLIFECYLE
