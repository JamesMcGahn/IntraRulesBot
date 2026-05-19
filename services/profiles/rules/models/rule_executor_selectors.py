from dataclasses import dataclass
from .rule_form_selectors import RuleFormSelectors
from .trigger_selectors import TriggerSelectors
from .condition_selectors import ConditionSelectors
from .action_selectors import ActionSelectors


@dataclass
class RuleExecutorSelectors:
    rule_form: RuleFormSelectors
    triggers: TriggerSelectors
    conditions: ConditionSelectors
    actions: ActionSelectors
