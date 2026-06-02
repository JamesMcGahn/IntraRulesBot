from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from ...queues.models import Queue
    from ...browser.ports import BrowserPort
    from ...logger.adapters import LogAdapter
    from ...profiles.models.browser_profile import BrowserProfile
    from .queue_progress_event import QueueProgressEvent


@dataclass(frozen=True)
class QueueExecutionContext:
    tenant: str
    browser_port: BrowserPort
    queue: Queue
    logger: LogAdapter
    should_stop: Callable[[], bool]
    profile: BrowserProfile
    progress_cb: Callable[[QueueProgressEvent], None]
