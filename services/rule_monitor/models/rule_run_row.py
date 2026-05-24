from dataclasses import dataclass
from ...rule_runner.enums import (
    RULEEXECSTATUS,
    RULERUNSTATUS,
    EXECUTORSCOPE,
    EXECUTORTASK,
)


@dataclass(slots=True)
class RuleRunRow:
    rule_guid: str
    rule_name: str
    status: RULERUNSTATUS | RULEEXECSTATUS
    scope: EXECUTORSCOPE
    task: EXECUTORTASK
    retry_count: int = 0
    index: int | None = None
    detail_type: str | None = None
    message: str | None = None
    started_at: int | None = None
    finished_at: int | None = None
