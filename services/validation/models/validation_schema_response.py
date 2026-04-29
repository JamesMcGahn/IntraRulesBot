from dataclasses import dataclass, field

from schemas.enums import SCHEMATYPE

from .validation_schema_error import SchemaError


@dataclass
class SchemaValidateResponse:
    schema_type: SCHEMATYPE
    valid: bool
    total_errors: int = 0
    errors: list[SchemaError] = field(default_factory=list)
