from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from services.monitor.models import RunSummary

from dataclasses import dataclass

P = TypeVar("P")


@dataclass
class MonitorSnapShotEvent(Generic[P]):
    rows: list[P]
    summary: RunSummary
