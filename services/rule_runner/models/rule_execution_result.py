from dataclasses import dataclass
from ..enums.rule_execution_status import RULEEXECSTATUS

from .executor_task_ref import ExecutorTaskRef


@dataclass
class RuleExecutionResult:
    rule_guid: str
    rule_name: str
    success: bool
    task_ref: ExecutorTaskRef
    status: RULEEXECSTATUS
    message: str = ""
