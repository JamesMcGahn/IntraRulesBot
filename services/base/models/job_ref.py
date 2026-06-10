from dataclasses import dataclass
from typing import Any

from ..enums import JOBSTATUS


# Event
@dataclass(frozen=True)
class JobRef:
    id: str
    task: Any
    status: JOBSTATUS
    error: str | None = None
