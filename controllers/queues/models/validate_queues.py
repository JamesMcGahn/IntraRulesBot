from __future__ import annotations

from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from services.files.models import ImportedSheetsRow
from dataclasses import dataclass, field


@dataclass
class ValidationQueues:
    provider_name: str
    provider_instance: str
    file_path: Path
    rows: list[ImportedSheetsRow] = field(default_factory=list)
