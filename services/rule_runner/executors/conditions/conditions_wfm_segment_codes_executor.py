from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState

    from ...models.executor_item_context import ExecutorItemContext
from ....rules.enums import QUEUESSOURCE

from ....rules.models.conditions import Condition, ConditionWFMSegmentCodesDetails
from ..base import BaseChildDetailedExecutor

from ...enums import EXECUTORSCOPE
from ....profiles.models.condition_selectors import ConditionDetailSelectors


class ConditionsWFMSegmentCodesExecutor(
    BaseChildDetailedExecutor[ConditionWFMSegmentCodesDetails, ConditionDetailSelectors]
):
    """
    Executor Condition Detail : Statistics
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: ConditionDetailSelectors,
        item_context: ExecutorItemContext[Condition[ConditionWFMSegmentCodesDetails]],
    ):
        super().__init__(
            EXECUTORSCOPE.CONDITION, context, state, selectors, item_context
        )
        self._flow = [
            self.set_equality_operator,
            self.set_equality_threshold,
            self.set_queues_sources_queue,
        ]

    def set_equality_operator(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition[ConditionWFMSegmentCodesDetails]],
    ) -> None:
        """
        Sets the equality operator for the stats-based condition.
        """
        self.logging(
            f"Selecting stats equality comparison operator for Condition {item_ctx.index+1}...",
            "INFO",
        )
        self.form_port.click(self.selectors.equality_operator_dropdown_arrow)

        # equality comparison operator selection
        self.form_port.select_exact_item_from_list(
            self.selectors.equality_operator_dropdown_items,
            item_ctx.item.details.equality_operator,
        )

    def set_equality_threshold(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition[ConditionStatsDetails]],
    ) -> None:
        """
        Sets the equality threshold for the stats-based condition.
        """
        self.logging(
            f"Selecting stats threshold for Condition {item_ctx.index+1}...", "INFO"
        )
        self.form_port.fill(
            self.selectors.equality_threshold_input,
            item_ctx.item.details.equality_threshold,
        )

    def set_queues_sources_queue(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition[ConditionStatsDetails]],
    ) -> None:
        """
        Sets the queue source for the condition to "queues" and selects all queues.
        """

        if item_ctx.item.details.queues_source != QUEUESSOURCE.QUEUES:
            return
        self.logging(
            f"Selecting queue source as 'queues' for Condition {item_ctx.index+1}...",
            "INFO",
        )
        self.form_port.click(self.selectors.queue_source_radio)

        self.logging(
            f"Selecting queue all listed queues for Condition {item_ctx.index+1}...",
            "INFO",
        )
        self.form_port.click(self.selectors.queue_dropdown_arrow)
        self.form_port.click_all_items_in_list(self.selectors.queue_dropdown_items)
