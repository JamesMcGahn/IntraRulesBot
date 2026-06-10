from dataclasses import dataclass

from schemas.enums import SCHEMATYPE


@dataclass
class SchemaValidatePayload:
    schema_type: SCHEMATYPE
    data: object
