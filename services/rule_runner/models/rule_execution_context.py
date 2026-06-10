from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from ...rules.models import Rule
    from ...browser.ports import BrowserPort
    from ...logger.adapters import LogAdapter
    from ...profiles.models.browser_profile import BrowserProfile
    from .rule_progress_event import RuleProgressEvent


@dataclass(frozen=True)
class RuleExecutionContext:
    tenant: str
    browser_port: BrowserPort
    rule: Rule
    logger: LogAdapter
    should_stop: Callable[[], bool]
    profile: BrowserProfile
    progress_cb: Callable[[RuleProgressEvent], None]
