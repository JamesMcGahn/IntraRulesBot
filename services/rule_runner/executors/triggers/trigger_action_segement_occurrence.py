from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState


from ...enums import EXECUTORSCOPE
from ..base import BaseChildDetailedExecutor
from ....profiles.models.trigger_selectors import TriggerDetailSelectors
from ....rules.models.triggers.action_based import SegmentOccurrenceDetails
from ...models.executor_item_context import ExecutorItemContext
from ....rules.models.triggers import ActionTrigger


class TriggerActionSegementOccurrenceExecutor(
    BaseChildDetailedExecutor[SegmentOccurrenceDetails, TriggerDetailSelectors]
):
    """
    Executor Trigger Detail : WFM: Segement Occurrence
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: TriggerDetailSelectors,
        item_context: ExecutorItemContext[ActionTrigger[SegmentOccurrenceDetails]],
    ):
        super().__init__(EXECUTORSCOPE.TRIGGER, context, state, selectors, item_context)
        self._flow = [
            self.set_segement_codes,
            self.set_lead_time,
            self.set_lookup_operator,
            self.set_segment_lookup,
            self.set_user_list,
        ]

    def set_segement_codes(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[SegmentOccurrenceDetails]],
    ) -> None:
        """
        Sets the segement codes from the list of provided segement codes.
        """
        self.logging(
            f"Setting the segement codes: {','.join(item_ctx.item.details.segment_codes)}"
        )

        for code in item_ctx.item.details.segment_codes:
            self.form_port.click(self.selectors.segment_code_dropdown_arrow)
            self.form_port.select_exact_item_from_list(
                self.selectors.segment_code_dropdown_items, code
            )
            self.form_port.click(self.selectors.segment_code_dropdown_arrow)

    def set_lead_time(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[SegmentOccurrenceDetails]],
    ) -> None:
        self.logging("Setting Lead time")
        self.form_port.fill(
            self.selectors.lead_time_input, item_ctx.item.details.lead_time
        )

    def set_lookup_operator(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[SegmentOccurrenceDetails]],
    ) -> None:
        self.logging("Setting Lookup Operator")
        self.form_port.click(self.selectors.lookup_operator_dropdown_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.lookup_operator_dropdown_items,
            item_ctx.item.details.lookup_operator,
        )

    def set_segment_lookup(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[SegmentOccurrenceDetails]],
    ) -> None:
        self.logging("Setting Segement Lookup")
        self.form_port.click(self.selectors.segment_lookup_dropdown_arrow)
        self.form_port.select_exact_item_from_list(
            self.selectors.segment_lookup_dropdown_items,
            item_ctx.item.details.segment_lookup,
        )

    def set_user_list(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ActionTrigger[SegmentOccurrenceDetails]],
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
