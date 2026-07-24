from dataclasses import dataclass, field
import time

from ..enums import QUEUEEXECSTATUS, QEXECUTORTASK, QUEUERUNSTATUS


@dataclass
class QueueProgressEvent:
    queue_guid: str
    queue_name: str
    queue_row: int
    status: QUEUEEXECSTATUS | QUEUERUNSTATUS
    task: QEXECUTORTASK | None
    retry_count: int = 0
    message: str | None = None
    started_at: int | None = None
    finished_at: int | None = None
    emitted_at: int = field(default_factory=time.monotonic_ns)
