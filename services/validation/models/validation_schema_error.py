from dataclasses import dataclass


@dataclass
class SchemaError:
    message: str
    error_path: str
    failed_field: str
