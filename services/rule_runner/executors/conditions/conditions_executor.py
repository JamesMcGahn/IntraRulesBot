from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState

from .conditions_stats_executor import ConditionsStatsExecutor
from ....rules.enums import CONDITIONDETAILTYPE
from ....rules.models.conditions import Condition
from ...enums import EXECUTORSCOPE
from ..base import BaseIterableScopeChildExecutor
from ...models.executor_item_context import ExecutorItemContext


class ConditionsExecutor(BaseIterableScopeChildExecutor[Condition]):
    """
    Executor class responsible for handling conditions within rules.
    """

    def __init__(self, context: RuleExecutionContext, state: RuleExecutionState):
        super().__init__(EXECUTORSCOPE.CONDITION, context, state)

        self._detail_type_registry = {
            CONDITIONDETAILTYPE.STATS: ConditionsStatsExecutor
        }

    def get_details_type(self, item: Condition) -> CONDITIONDETAILTYPE:
        return item.details.condition_type

    def get_items(self) -> list[Condition]:
        return self._ctx.rule.conditions

    def set_provider_category(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition],
    ) -> None:
        """
        Selects the provider category for the specified condition.
        """
        self.logging(
            f"Selecting provider category for Condition {item_ctx.index+1}...", "INFO"
        )

        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.conditions.common.provider_category_items,
            item_ctx.item.provider_category,
        )

    def set_provider_instance(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition],
    ) -> None:
        """
        Selects the provider instance for the specified condition.
        """
        self.logging(
            f"Selecting provider instance for Condition {item_ctx.index+1}...", "INFO"
        )
        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.conditions.common.provider_instance_items,
            item_ctx.item.provider_instance,
        )

    def set_provider_condition(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition],
    ) -> None:
        """
        Selects the provider condition for the specified condition.
        """
        self.logging(
            f"Selecting condition selection for Condition {item_ctx.index+1}...", "INFO"
        )
        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.conditions.common.provider_condition_items,
            item_ctx.item.provider_condition,
        )

    def execute_details_type(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition],
    ) -> None:
        executor = self.detail_type_registry.get(item_ctx.detail_type)
        if not executor:
            msg = f"{item_ctx.detail_type} is not a supported trigger action"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)
        self.logging(f"Moving to {item_ctx.detail_type.value} detail page.", "INFO")
        selectors = ctx.profile.selectors.conditions.details.get(item_ctx.detail_type)
        if selectors is None:
            msg = f"{item_ctx.detail_type.value} is does not have selectors implemented"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)
        executor(ctx, state, selectors, item_ctx).execute()

    def add_next_item(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Condition],
    ) -> None:
        """
        Adds additional conditions to the UI if more than one condition exists.
        """
        if (
            item_ctx.index != len(ctx.rule.conditions) - 1
            and len(ctx.rule.conditions) > 1
        ):
            self.logging(f"Adding condition {item_ctx.index+2}...", "INFO")
            self.form_port.click(
                ctx.profile.selectors.conditions.common.add_condition_button
            )
