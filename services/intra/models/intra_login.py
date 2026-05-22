from dataclasses import dataclass
from base.enums import INTRAVERSION


@dataclass
class IntraLogin:
    user_name: str
    password: str
    tenant: str
    platform_version: INTRAVERSION
