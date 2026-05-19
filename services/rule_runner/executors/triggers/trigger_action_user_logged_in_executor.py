from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState


from ...enums import EXECUTORSCOPE
from ..base import BaseChildDetailedExecutor
from ....profiles.rules.models.trigger_selectors import TriggerDetailSelectors
from ....rules.models.triggers.action_based import AgentLoggedInDetails
from ...models.executor_item_context import ExecutorItemContext
from ....rules.models.triggers import ActionTrigger


class TriggerActionUserLoggedInExecutor(
    BaseChildDetailedExecutor[AgentLoggedInDetails, TriggerDetailSelectors]
):
    """
    Executor Trigger Detail : State Changed
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: TriggerDetailSelectors,
        item_context: ExecutorItemContext[ActionTrigger[AgentLoggedInDetails]],
    ):
        super().__init__(EXECUTORSCOPE.TRIGGER, context, state, selectors, item_context)
        self._flow = [
            self.set_user_list,
        ]

    def set_user_list(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentLoggedInDetails]],
    ) -> None:
        """
        Sets the user list for the state changed to rule.
        """
        self.form_port.click(self.selectors.user_list_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.user_list_items,
            item_ctx.item.details.user_list,
        )
