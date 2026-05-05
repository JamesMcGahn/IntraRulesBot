from dataclasses import dataclass


@dataclass
class RuleRunnerConfig:
    user_name: str
    password: str
    tenant: str
    platform_version: str
