from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState

from .trigger_action_state_changed_executor import TriggerActionStateChangedExecutor
from ....rules.enums import ACTIONTRIGGERDETAILTYPE
from ...enums import EXECUTORSCOPE

from ..base import BaseScopeChildExecutor
from ...models.executor_item_context import ExecutorItemContext


class TriggerActionBasedExectuor(BaseScopeChildExecutor):
    """
    Executor Trigger : Action Based Triggers
    """

    def __init__(self, context: RuleExecutionContext, state: RuleExecutionState):
        super().__init__(EXECUTORSCOPE.TRIGGER, context, state)

        self._detail_type_registry = {
            ACTIONTRIGGERDETAILTYPE.STATE_CHANGED: TriggerActionStateChangedExecutor
        }

    def set_provider_category(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Selects the provider category for the specified action.
        """
        self.logging("Selecting provider category for Action Trigger", "INFO")
        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.triggers.common.provider_category_items,
            ctx.rule.trigger.provider_category,
        )

    def set_provider_instance(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Selects the provider instance for the specified condition.
        """
        self.logging("Selecting provider instance for Action Trigger", "INFO")
        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.triggers.common.provider_instance_items,
            ctx.rule.trigger.provider_instance,
        )

    def set_provider_condition(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Selects the provider condition for the specified condition.
        """
        self.logging("Selecting condition selection for Action Trigger", "INFO")

        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.triggers.common.provider_condition_items,
            ctx.rule.trigger.provider_condition,
        )

    def execute_details_type(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ):
        action_type = ctx.rule.trigger.details.action_type
        executor = self.detail_type_registry.get(action_type)
        if not executor:
            msg = f"{action_type.value} is not a supported trigger action"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)
        self.logging(f"Moving to {action_type.value} detail page.", "INFO")
        selectors = ctx.profile.selectors.triggers.details.get(action_type)
        if selectors is None:
            msg = f"{action_type.value} is does not have selectors implemented"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)

        item = ExecutorItemContext(
            ctx.rule.trigger, ctx.rule.trigger.details.action_type, 0
        )
        executor(ctx, state, selectors, item).execute()
