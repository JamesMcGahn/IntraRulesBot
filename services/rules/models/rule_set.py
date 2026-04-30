from dataclasses import dataclass, field
from ..enums import RULECATEGORY
from .triggers import FrequencyTrigger
from .triggers.action_based import ActionTrigger
from .conditions import Condition
from .actions import Action


@dataclass
class RuleSet:
    rule_set_name: str
    guid: str
    description: str = ""
    rules_guids: list[str] = field(default_factory=list)
