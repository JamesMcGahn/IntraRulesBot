from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from ...rules.models import Rule
    from ...browser.ports import BrowserPort, InteractionPort
    from ...logger.adapters import LogAdapter


@dataclass(frozen=True)
class RuleExecutionContext:
    tenant: str
    browser_port: BrowserPort
    interaction_port: InteractionPort | None
    rule: Rule
    logger: LogAdapter
    should_stop: Callable[[], bool]
    rule_name: str
    rule_rename_attempts: int = 0
