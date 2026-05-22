from dataclasses import dataclass
from .rule_form_selectors import RuleFormSelectors
from .trigger_selectors import TriggerSelectors
from .condition_selectors import ConditionSelectors
from .action_selectors import ActionSelectors
from .login_selectors import LoginSelectors


@dataclass
class ExecutorSelectors:
    rule_form: RuleFormSelectors
    triggers: TriggerSelectors
    conditions: ConditionSelectors
    actions: ActionSelectors
    login: LoginSelectors
