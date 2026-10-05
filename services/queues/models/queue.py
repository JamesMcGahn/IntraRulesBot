from dataclasses import dataclass
from ..enums.queue_action import QUEUEACTION


@dataclass
class Queue:
    guid: str
    queue_name: str
    queue_number: str
    row_number: int
    provider_name: str
    provider_instance: str
    action_type: QUEUEACTION = QUEUEACTION.ADD
