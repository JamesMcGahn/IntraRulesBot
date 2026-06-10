from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation.models import SchemaError
from dataclasses import dataclass


@dataclass
class ValidationRulesResult:
    errors_by_rule: dict[str, list[SchemaError]]
