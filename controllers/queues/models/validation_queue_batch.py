from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation.models import SchemaError
    from ..enums import VALIDATIONBATCHTYPE
    from services.rules.models import Rule
from dataclasses import dataclass, field


@dataclass
class ValidationQueueBatch:
    batch_type: VALIDATIONBATCHTYPE
    batch_name: str
    batch_id: str
    batch_total: int = 0
    validation_total: int = 0
    valid_queues: list[Rule] = field(default_factory=list)
    invalid_queues: list[Rule] = field(default_factory=list)
    total_errors: int = 0
    errors: list[SchemaError] = field(default_factory=list)
    file_path: str = ""
