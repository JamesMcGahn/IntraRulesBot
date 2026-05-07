from dataclasses import dataclass


@dataclass
class IntraLogin:
    user_name: str
    password: str
    tenant: str
    platform_version: str
