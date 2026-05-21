from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState


from ....rules.enums import STATEEQUALITYOPERATOR
from ...enums import EXECUTORSCOPE
from ..base import BaseChildDetailedExecutor
from ....profiles.rules.models.trigger_selectors import TriggerDetailSelectors
from ....rules.models.triggers.action_based import AgentStateChangeDetails
from ...models.executor_item_context import ExecutorItemContext
from ....rules.models.triggers import ActionTrigger


class TriggerActionStateChangedExecutor(
    BaseChildDetailedExecutor[AgentStateChangeDetails, TriggerDetailSelectors]
):
    """
    Executor Trigger Detail : State Changed
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: TriggerDetailSelectors,
        item_context: ExecutorItemContext[ActionTrigger[AgentStateChangeDetails]],
    ):
        super().__init__(EXECUTORSCOPE.TRIGGER, context, state, selectors, item_context)
        self._flow = [
            self.set_agent_and_aux,
            self.set_equality_operator,
            self.set_user_list,
        ]

    def set_state_changed_to(self, state: str) -> None:
        self.form_port.click(self.selectors.state_dropdown_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.state_dropdown_items,
            state,
        )

    def set_agent_aux(self, aux: str) -> None:
        """
        Sets the the aux code for the state changed to.
        """
        self.form_port.fill(self.selectors.aux_input, aux)

    def set_agent_and_aux(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentStateChangeDetails]],
    ) -> None:
        """
        Sets the agent state and aux code for the state changed to for the array of state.
        """
        self.logging("Setting the state and aux.")
        for agent_changed in item_ctx.item.details.state:
            self.set_state_changed_to(agent_changed.state)
            self.set_agent_aux(agent_changed.aux)

            self.form_port.click(self.selectors.add_state_button)

    def set_equality_operator(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentStateChangeDetails]],
    ) -> None:
        """
        Sets the the equality operator for the state changed to.
        """

        equality_operator = item_ctx.item.details.equality_operator
        self.logging(
            f"Setting equality operator to {equality_operator}.",
            "INFO",
        )
        if equality_operator == STATEEQUALITYOPERATOR.EQUAL_TO:
            self.form_port.click(self.selectors.equal_to_radio)

        elif equality_operator == STATEEQUALITYOPERATOR.NOT_EQUAL_TO:
            self.form_port.click(self.selectors.not_equal_to_radio)

    def set_user_list(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentStateChangeDetails]],
    ) -> None:
        """
        Sets the user list for the state changed to rule.
        """
        self.logging("Setting the user list.")
        self.form_port.click(self.selectors.user_list_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.user_list_items,
            item_ctx.item.details.user_list,
        )
