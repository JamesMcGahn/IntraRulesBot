from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.validation.models import SchemaError
    from ..enums import VALIDATIONBATCHTYPE
    from services.files.models import ImportedSheetsRow
from dataclasses import dataclass, field


@dataclass
class ValidationQueueBatch:
    batch_type: VALIDATIONBATCHTYPE
    provider_name: str
    provider_instance: str
    batch_name: str
    batch_id: str
    batch_total: int = 0
    validation_total: int = 0
    valid_queues: list[ImportedSheetsRow] = field(default_factory=list)
    invalid_queues: list[ImportedSheetsRow] = field(default_factory=list)
    total_errors: int = 0
    errors: list[SchemaError] = field(default_factory=list)
    file_path: str = ""
