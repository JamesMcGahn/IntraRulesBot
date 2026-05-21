from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState

import secrets
from ...enums import EXECUTORSCOPE
from ..base import BaseChildDetailedExecutor
from ....profiles.rules.models.trigger_selectors import TriggerDetailSelectors
from ....rules.models.triggers.action_based import IntraQuickActionClicked
from ...models.executor_item_context import ExecutorItemContext
from ....rules.models.triggers import ActionTrigger


class TriggerQuickActionExecutor(
    BaseChildDetailedExecutor[IntraQuickActionClicked, TriggerDetailSelectors]
):
    """
    Executor Trigger Detail : Logged Out
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: TriggerDetailSelectors,
        item_context: ExecutorItemContext[ActionTrigger[IntraQuickActionClicked]],
    ):
        super().__init__(EXECUTORSCOPE.TRIGGER, context, state, selectors, item_context)
        self._flow = [
            self.select_action_icon,
            self.set_quick_action_name,
        ]

    def set_quick_action_name(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[IntraQuickActionClicked]],
    ) -> None:
        """
        Sets the user list for the state changed to rule.
        """
        self.logging("Setting the quick action name.")
        self.form_port.fill(
            self.selectors.quick_action_name_input,
            f"{item_ctx.item.details.quick_action_name}-{secrets.token_hex(4)}",
        )

    def select_action_icon(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[IntraQuickActionClicked]],
    ) -> None:
        self.logging("Setting Quick Action Icon")
        self.form_port.click_first_child(self.selectors.quick_action_icon_container)
