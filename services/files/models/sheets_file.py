from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ImportedSheetsRow:
    row_number: int
    values: dict[str, Any]


@dataclass(frozen=True)
class SheetsLoadResult:
    ok: bool
    file_path: Path
    rows: list[ImportedSheetsRow] = field(default_factory=list)
    message: str | None = None
