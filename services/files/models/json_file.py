from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class JSONLoadResult:
    ok: bool
    data: dict[str, Any] | list[Any] | None
    file_path: Path
    message: str | None = None


@dataclass(frozen=True)
class JSONSaveResult:
    ok: bool
    file_path: Path
    message: str | None = None
