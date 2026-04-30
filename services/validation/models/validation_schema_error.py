from dataclasses import dataclass


@dataclass
class SchemaError:
    rule_name: str
    message: str
    error_path: str
    failed_field: str
