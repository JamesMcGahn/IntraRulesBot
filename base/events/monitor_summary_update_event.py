from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.monitor.models import RunSummary
from dataclasses import dataclass


@dataclass
class MonitorSummaryUpdateEvent:
    summary: RunSummary
