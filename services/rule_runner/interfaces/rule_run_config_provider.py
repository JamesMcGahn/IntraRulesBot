from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ..models import RuleRunnerConfig


class RuleRunnerConfigProvider(Protocol):
    def get_rule_run_config(self) -> "RuleRunnerConfig": ...
