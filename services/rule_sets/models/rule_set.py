from dataclasses import dataclass, field
from ...rules.models import Rule


@dataclass
class RuleSet:
    rule_set_name: str
    guid: str
    description: str = ""
    default: bool = False
    rules: list[Rule] = field(default_factory=list)
