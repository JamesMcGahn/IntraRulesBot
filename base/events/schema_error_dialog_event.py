from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation.models import SchemaError
from dataclasses import dataclass, field


@dataclass
class SchemaErrorDialogEvent:
    errors: list[SchemaError] = field(default_factory=list)
