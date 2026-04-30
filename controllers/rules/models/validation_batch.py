from dataclasses import dataclass, field

from services.validation.models import SchemaError


@dataclass
class ValidationBatch:
    rule_batch_name: str
    rule_batch_description: str
    batch_id: str
    batch_total: int = 0
    validation_total: int = 0
    valid_rules: list = field(default_factory=list)
    invalid_rules: list = field(default_factory=list)
    total_errors: int = 0
    rule_errors: list[SchemaError] = field(default_factory=list)
