from dataclasses import dataclass
from base.enums import INTRAVERSION


@dataclass
class RuleRunnerConfig:
    user_name: str
    password: str
    tenant: str
    platform_version: INTRAVERSION
    login_valid: bool
