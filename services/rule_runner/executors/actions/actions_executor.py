from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....rules.models.actions import Action
    from ...models import RuleExecutionContext, RuleExecutionState


from .actions_email_executor import ActionsEmailExecutor
from ....rules.enums import ACTIONDETAILTYPE

from ..base import BaseIterableScopeChildExecutor
from ....rules.models.actions import Action
from ...enums import EXECUTORSCOPE
from ...models.executor_item_context import ExecutorItemContext


class ActionsExecutor(BaseIterableScopeChildExecutor[Action]):
    """
    Executor class responsible for handling multiple actions within rules.
    """

    def __init__(self, context: RuleExecutionContext, state: RuleExecutionState):
        super().__init__(EXECUTORSCOPE.ACTION, context, state)

        self._detail_type_registry = {ACTIONDETAILTYPE.EMAIL: ActionsEmailExecutor}

    def get_details_type(self, item: Action) -> ACTIONDETAILTYPE:
        return item.details.action_type

    def get_items(self) -> list[Action]:
        return self._ctx.rule.actions

    def set_provider_category(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action],
    ) -> None:
        """
        Selects the provider category for the specified action.
        """
        self.logging(
            f"Selecting provider category for Action {item_ctx.index+1}...", "INFO"
        )
        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.actions.common.provider_category_items,
            item_ctx.item.provider_category,
        )

    def set_provider_instance(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action],
    ) -> None:
        """
        Selects the provider instance for the specified action.
        """
        self.logging(
            f"Selecting provider instance for Action {item_ctx.index+1}...", "INFO"
        )

        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.actions.common.provider_instance_items,
            item_ctx.item.provider_instance,
        )

    def set_provider_condition(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action],
    ) -> None:
        """
        Selects the provider condition for the specified action.
        """
        self.logging(
            f"Selecting condition selection for Action {item_ctx.index+1}...", "INFO"
        )
        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.actions.common.provider_condition_items,
            item_ctx.item.provider_condition,
        )

    def execute_details_type(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action],
    ) -> None:
        executor = self.detail_type_registry.get(item_ctx.detail_type)
        if not executor:
            msg = f"{item_ctx.detail_type} is not a supported trigger action"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)
        self.logging(f"Moving to {item_ctx.detail_type.value} detail page.", "INFO")
        selectors = ctx.profile.selectors.actions.details.get(item_ctx.detail_type)
        if selectors is None:
            msg = f"{item_ctx.detail_type.value} is does not have selectors implemented"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)
        executor(ctx, state, selectors, item_ctx).execute()

    def add_next_item(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action],
    ) -> None:
        """
        Adds additional actions to the UI if more than one action exists.
        """
        if item_ctx.index != len(ctx.rule.actions) - 1 and len(ctx.rule.actions) > 1:
            self.logging(f"Adding condition {item_ctx.index+2}...", "INFO")
            self.form_port.click(ctx.profile.selectors.actions.common.add_action_button)
