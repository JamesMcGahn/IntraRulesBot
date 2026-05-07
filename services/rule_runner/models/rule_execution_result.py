from dataclasses import dataclass
from ..enums.rule_execution_status import RULEEXECSTATUS


@dataclass
class RuleExecutionResult:
    rule_guid: str
    rule_name: str
    success: bool
    status: RULEEXECSTATUS
    message: str = ""
