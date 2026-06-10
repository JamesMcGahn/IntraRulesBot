from dataclasses import dataclass
from ..enums import QUEUERUNSTATUS
from ...queues.models import Queue


@dataclass
class QueueRunItem:
    guid: str
    queue: Queue
    status: QUEUERUNSTATUS = QUEUERUNSTATUS.PENDING
    retry_count: int = 0
