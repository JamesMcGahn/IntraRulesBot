from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState


from ...enums import EXECUTORSCOPE
from ..base import BaseChildDetailedExecutor
from ....profiles.rules.models.trigger_selectors import TriggerDetailSelectors
from ....rules.models.triggers.action_based import AgentTimeInStateDetails
from ...models.executor_item_context import ExecutorItemContext
from ....rules.models.triggers import ActionTrigger


class TriggerTimeInStateExecutor(
    BaseChildDetailedExecutor[AgentTimeInStateDetails, TriggerDetailSelectors]
):
    """
    Executor Trigger Detail : State Changed
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: TriggerDetailSelectors,
        item_context: ExecutorItemContext[ActionTrigger[AgentTimeInStateDetails]],
    ):
        super().__init__(EXECUTORSCOPE.TRIGGER, context, state, selectors, item_context)
        self._flow = [
            self.set_agent_and_aux,
            self.set_state_equality_operator,
            self.set_state_equality_threshold,
            self.set_user_list,
        ]

    def set_state_changed_to(self, state: str) -> None:
        self.form_port.click(self.selectors.state_dropdown_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.state_dropdown_items,
            state,
        )
        self.form_port.click(self.selectors.state_dropdown_arrow)

    def set_agent_aux(self, aux: str) -> None:
        """
        Sets the the aux code for the state changed to.
        """
        self.form_port.fill(self.selectors.aux_input, aux)

    def set_agent_and_aux(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentTimeInStateDetails]],
    ) -> None:
        """
        Sets the agent state and aux code for the state changed to for the array of state.
        """
        state_length = len(item_ctx.item.details.state)
        self.logging(f"Selecting state: {state_length} items")
        for index, agent_changed in enumerate(item_ctx.item.details.state):
            if state_length == 1 and index == 0:
                self.set_aux_equality_operator(ctx, state, item_ctx)
                self.set_agent_aux(agent_changed.aux)

            self.set_state_changed_to(agent_changed.state)

    def set_aux_equality_operator(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentTimeInStateDetails]],
    ) -> None:
        equality_operator = item_ctx.item.details.aux_equality_operator
        self.logging(
            f"Setting aux equality operator to {equality_operator}.",
            "INFO",
        )
        self.form_port.click(self.selectors.aux_equality_operator_dropdown_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.aux_equality_operator_dropdown_items,
            item_ctx.item.details.aux_equality_operator,
        )

    def set_state_equality_operator(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentTimeInStateDetails]],
    ) -> None:
        """
        Sets the the equality operator for the state changed to.
        """

        equality_operator = item_ctx.item.details.equality_operator
        self.logging(
            f"Setting equality operator to {equality_operator}.",
            "INFO",
        )
        self.form_port.click(self.selectors.state_equality_operator_dropdown_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.state_equality_operator_dropdown_items,
            item_ctx.item.details.equality_operator,
        )

    def set_state_equality_threshold(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentTimeInStateDetails]],
    ) -> None:
        """
        Sets the the equality operator for the state changed to.
        """
        self.logging("Setting state equality threshold")
        self.form_port.fill(
            self.selectors.state_equality_threshold_input,
            item_ctx.item.details.equality_threshold,
        )

    def set_user_list(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[AgentTimeInStateDetails]],
    ) -> None:
        """
        Sets the user list for the state changed to rule.
        """
        self.form_port.click(self.selectors.user_list_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.user_list_items,
            item_ctx.item.details.user_list,
        )
