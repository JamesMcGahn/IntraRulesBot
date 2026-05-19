from dataclasses import dataclass
from typing import Callable
from ..enums import EXECUTORTASK


@dataclass(frozen=True)
class EXECSTEPCALL:
    task: EXECUTORTASK
    handler: Callable[..., None]
