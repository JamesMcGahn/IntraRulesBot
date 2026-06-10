from dataclasses import dataclass, field
from .rule_rule_item import RuleRunItem
from .rule_run_config import RuleRunnerConfig


@dataclass
class RuleRunnerRequestPayload:
    config: RuleRunnerConfig
    rules: list[RuleRunItem] = field(default_factory=list)
