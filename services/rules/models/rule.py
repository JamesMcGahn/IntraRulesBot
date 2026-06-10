from dataclasses import dataclass, field
from ..enums import RULECATEGORY
from .triggers import FrequencyTrigger
from .triggers.action_based import ActionTrigger
from .conditions import Condition
from .actions import Action


@dataclass
class Rule:
    rule_name: str
    guid: str
    rule_category: RULECATEGORY
    trigger: FrequencyTrigger | ActionTrigger
    conditions: list[Condition] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
