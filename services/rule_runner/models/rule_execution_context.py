from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from ...rules.models import Rule
    from ...browser.ports import BrowserPort
    from ...logger.adapters import LogAdapter
    from .rule_path_profile import RulePathProfile


@dataclass(frozen=True)
class RuleExecutionContext:
    tenant: str
    browser_port: BrowserPort
    rule: Rule
    logger: LogAdapter
    should_stop: Callable[[], bool]
    profile: RulePathProfile
