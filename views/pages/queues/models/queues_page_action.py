from dataclasses import dataclass
from typing import Generic, TypeVar

from ..enums.queues_page_event import QUEUESPAGEEVENT

T = TypeVar("T")


@dataclass(frozen=True)
class QueuesPageAction(Generic[T]):
    event: QUEUESPAGEEVENT
    data: T
