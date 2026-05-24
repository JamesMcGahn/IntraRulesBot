from dataclasses import dataclass

from ..enums.rule_execution_status import RULEEXECSTATUS
from .executor_task_ref import ExecutorTaskRef


@dataclass
class RuleProgressEvent:
    rule_guid: str
    rule_name: str
    task_ref: ExecutorTaskRef | None
    status: RULEEXECSTATUS
    message: str | None = None
