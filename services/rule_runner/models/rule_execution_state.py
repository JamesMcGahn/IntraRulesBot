from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ...browser.ports import InteractionPort
    from .executor_task_ref import ExecutorTaskRef


@dataclass
class RuleExecutionState:
    form_port: InteractionPort | None
    rule_name: str
    current_task: ExecutorTaskRef
    rule_rename_attempts: int = 0
