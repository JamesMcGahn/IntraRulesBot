from dataclasses import dataclass
from ....queue_runner.enums import (
    QUEUEEXECSTATUS,
    QUEUERUNSTATUS,
    QEXECUTORTASK,
)


@dataclass(slots=True)
class QueueRunRow:
    queue_guid: str
    queue_row: str
    queue_name: str
    status: QUEUERUNSTATUS | QUEUEEXECSTATUS
    task: QEXECUTORTASK
    retry_count: int = 0
    message: str | None = None
    started_at: int | None = None
    finished_at: int | None = None
