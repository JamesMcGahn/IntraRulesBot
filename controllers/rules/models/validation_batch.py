from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation.models import SchemaError
    from ..enums import VALIDATIONBATCHTYPE
    from services.rules.models import Rule
from dataclasses import dataclass, field


@dataclass
class ValidationBatch:
    batch_type: VALIDATIONBATCHTYPE
    rule_batch_name: str
    rule_batch_description: str
    batch_id: str
    batch_total: int = 0
    validation_total: int = 0
    valid_rules: list[Rule] = field(default_factory=list)
    invalid_rules: list[Rule] = field(default_factory=list)
    total_errors: int = 0
    rule_errors: list[SchemaError] = field(default_factory=list)
    file_path: str = ""
