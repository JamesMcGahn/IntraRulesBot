from dataclasses import dataclass, field
from services.validation.models import SchemaError


@dataclass
class SchemaErrorDialogEvent:
    errors: list[SchemaError] = field(default_factory=list)
