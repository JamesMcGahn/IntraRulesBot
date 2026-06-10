from dataclasses import dataclass


@dataclass
class SchemaError:
    name: str
    guid: str
    message: str
    error_path: str
    error_path_msg: str
    failed_field: str
