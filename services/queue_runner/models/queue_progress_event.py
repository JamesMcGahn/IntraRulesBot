from dataclasses import dataclass

from ..enums import QUEUEEXECSTATUS, QEXECUTORTASK, QUEUERUNSTATUS


@dataclass
class QueueProgressEvent:
    queue_guid: str
    queue_name: str
    queue_row: int
    status: QUEUEEXECSTATUS | QUEUERUNSTATUS
    task: QEXECUTORTASK | None
    message: str | None = None
    started_at: int | None = None
    finished_at: int | None = None
