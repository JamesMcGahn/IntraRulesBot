from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProgressStatus:
    current_value: int
    total: int
