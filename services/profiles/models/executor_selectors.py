from dataclasses import dataclass

from .action_selectors import ActionSelectors
from .condition_selectors import ConditionSelectors
from .login_selectors import LoginSelectors
from .provider_instance_selectors import ProviderInstanceSelectors
from .providers_selectors import ProviderSelectors
from .queue_selectors import QueueSelectors
from .rule_form_selectors import RuleFormSelectors
from .trigger_selectors import TriggerSelectors


@dataclass
class ExecutorSelectors:
    rule_form: RuleFormSelectors
    triggers: TriggerSelectors
    conditions: ConditionSelectors
    actions: ActionSelectors
    login: LoginSelectors
    providers: ProviderSelectors
    provider_instance: ProviderInstanceSelectors
    queues: QueueSelectors
