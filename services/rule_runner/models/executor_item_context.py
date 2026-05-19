from typing import Generic, TypeVar
from dataclasses import dataclass
from enum import Enum

ItemT = TypeVar("ItemT")


@dataclass(frozen=True)
class ExecutorItemContext(Generic[ItemT]):
    item: ItemT
    detail_type: Enum
    index: int | None = None
