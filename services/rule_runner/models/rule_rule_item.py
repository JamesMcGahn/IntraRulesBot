from dataclasses import dataclass
from ..enums.rule_run_status import RULERUNSTATUS
from services.rules.models import Rule


@dataclass
class RuleRunItem:
    rule_guid: str
    rule: Rule
    status: RULERUNSTATUS = RULERUNSTATUS.PENDING
    retry_count: int = 0
