from dataclasses import dataclass
from ..enums import QUEUEEXECSTATUS, QEXECUTORTASK


@dataclass
class QueueExecutionResult:
    queue_guid: str
    queue_name: str
    queue_row: int
    success: bool
    task: QEXECUTORTASK
    status: QUEUEEXECSTATUS
    message: str = ""
