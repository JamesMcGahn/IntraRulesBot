from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...browser.ports import BrowserPort
    from ...logger.adapters import LogAdapter
    from ...profiles.models.browser_profile import BrowserProfile
    from ...queues.models import Queue
    from .queue_progress_event import QueueProgressEvent
    from .queue_runner_state import QueueRunnerState


@dataclass(frozen=True)
class QueueExecutionContext:
    tenant: str
    provider_name: str
    provider_instance: str
    browser_port: BrowserPort
    state: QueueRunnerState
    queue: Queue
    logger: LogAdapter
    should_stop: Callable[[], bool]
    profile: BrowserProfile
    progress_cb: Callable[[QueueProgressEvent], None]
