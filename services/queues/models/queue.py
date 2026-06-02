from dataclasses import dataclass


@dataclass
class Queue:
    guid: str
    queue_name: str
    queue_number: str
    row_number: int
