from ..enums import EXECUTORTASK, EXECUTORSCOPE
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutorTaskRef:
    scope: EXECUTORSCOPE
    task: EXECUTORTASK
    index: int | None = None
    detail_type: str | None = None
