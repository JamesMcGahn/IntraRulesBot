from dataclasses import dataclass, field
from .rule_rule_item import RuleRunItem


@dataclass
class RuleRunnerResponse:
    success: bool
    completed_count: int
    total_count: int
    errored_items: list[RuleRunItem] = field(default_factory=list)
    successful_items: list[RuleRunItem] = field(default_factory=list)
