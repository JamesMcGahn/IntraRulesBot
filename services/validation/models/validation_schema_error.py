from dataclasses import dataclass


@dataclass
class SchemaError:
    rule_name: str
    rule_guid: str
    message: str
    error_path: str
    error_path_msg: str
    failed_field: str
