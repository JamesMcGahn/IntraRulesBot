from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ...browser.ports import InteractionPort
    from .executor_task_ref import ExecutorTaskRef
    from ..enums import RULEEXECSTATUS


@dataclass
class RuleExecutionState:
    status: RULEEXECSTATUS
    interaction_port: InteractionPort | None
    rule_name: str
    current_task: ExecutorTaskRef
    rule_rename_attempts: int = 0
