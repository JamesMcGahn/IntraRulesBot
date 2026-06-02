from dataclasses import dataclass

from ..enums import QUEUEEXECSTATUS, QEXECUTORTASK


@dataclass
class QueueProgressEvent:
    queue_guid: str
    queue_name: str
    queue_row: int
    status: QUEUEEXECSTATUS
    task: QEXECUTORTASK | None
    message: str | None = None
    started_at: int | None = None
    finished_at: int | None = None
