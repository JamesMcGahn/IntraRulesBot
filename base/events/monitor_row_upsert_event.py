from __future__ import annotations

from typing import Generic, TypeVar
from dataclasses import dataclass

P = TypeVar("P")


@dataclass
class MonitorRowUpsertEvent(Generic[P]):
    row: P
