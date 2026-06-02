from dataclasses import dataclass
from typing import Callable
from ..enums import QEXECUTORTASK


@dataclass(frozen=True)
class QEXECSTEPCALL:
    task: QEXECUTORTASK
    handler: Callable[..., None]
