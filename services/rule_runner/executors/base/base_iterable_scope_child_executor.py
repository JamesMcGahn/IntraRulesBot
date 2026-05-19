from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState
import threading
from ..wrappers import ExecutorWrappers
from ...enums import EXECUTORSCOPE, EXECUTORTASK, RULEEXECSTATUS
from ...models import EXECSTEPCALL
from ..base import BaseScopeExecutor
from ...models.executor_item_context import ExecutorItemContext
from ...errors import StoppedRequestException
from enum import Enum

ItemT = TypeVar("ItemT")


class BaseIterableScopeChildExecutor(BaseScopeExecutor, Generic[ItemT]):
    """
    Base scope child is responsible for handling common selections and then executing the detailed executor.
    """

    def __init__(
        self,
        scope_id: EXECUTORSCOPE,
        context: RuleExecutionContext,
        state: RuleExecutionState,
    ):
        super().__init__(scope_id, context, state)
        self._flow = [
            EXECSTEPCALL(
                EXECUTORTASK.SET_PROVIDER_CATEGORY, self.set_provider_category
            ),
            EXECSTEPCALL(
                EXECUTORTASK.SET_PROVIDER_INSTANCE, self.set_provider_instance
            ),
            EXECSTEPCALL(
                EXECUTORTASK.SET_PROVIDER_CONDITION, self.set_provider_condition
            ),
            EXECSTEPCALL(EXECUTORTASK.EXECUTE_DETAIL, self.execute_details_type),
            EXECSTEPCALL(EXECUTORTASK.ADD_NEXT_ITEM, self.add_next_item),
        ]
        self._detail_type_registry = None

    @property
    def detail_type_registry(self) -> dict:

        if self._detail_type_registry is None:

            raise RuntimeError("Detail type registry has not been initialized")

        return self._detail_type_registry

    def get_details_type(self, item: ItemT) -> Enum:
        msg = f"{self.__class__.__name__} has not implemented get_details_type"
        self.logging(msg)
        raise NotImplementedError(msg)

    def get_items(self) -> list[ItemT]:
        msg = f"{self.__class__.__name__} has not implemented get_items"
        self.logging(msg)
        raise NotImplementedError(msg)

    def run_child_step(self, step: EXECSTEPCALL, item_ctx: ExecutorItemContext[ItemT]):

        ref = self.task_ref(step.task, item_ctx.index, item_ctx.detail_type)
        self.set_state_status(ref, RULEEXECSTATUS.RUNNING)
        if self._ctx.should_stop():
            self.set_state_status(ref, RULEEXECSTATUS.RUNNER_STOPPED_ERROR)
            raise StoppedRequestException("Stop Requested")
        try:
            handler = step.handler
            handler(self._ctx, self._state, item_ctx)
        except Exception as e:
            if self._ctx.should_stop():
                self.set_state_status(ref, RULEEXECSTATUS.RUNNER_STOPPED_ERROR)
                raise StoppedRequestException("Stop Requested") from e

            self.set_state_status(ref, RULEEXECSTATUS.UNKNOWN_ERROR)
            raise
        self.set_state_status(ref, RULEEXECSTATUS.SUCCESS)

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process each Rule Scope within the rule, including setting
        provider categories, instances, conditions, and executing child executor detailed actions.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        for index, item in enumerate(self.get_items()):
            item_ctx = ExecutorItemContext[ItemT](
                item=item, index=index, detail_type=self.get_details_type(item)
            )
            for step in self._flow:
                self.run_child_step(step, item_ctx)

    def set_provider_category(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ItemT],
    ) -> None:
        """
        Selects the provider category.
        """
        msg = f"{self.__class__.__name__} has not implemented set_provider_category"
        self.logging(msg)
        raise NotImplementedError(msg)

    def set_provider_instance(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ItemT],
    ) -> None:
        """
        Selects the provider instance.
        """
        msg = f"{self.__class__.__name__} has not implemented set_provider_instance"
        self.logging(msg)
        raise NotImplementedError(msg)

    def set_provider_condition(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ItemT],
    ) -> None:
        """
        Selects the provider condition.
        """
        msg = f"{self.__class__.__name__} has not implemented set_provider_condition"
        self.logging(msg)
        raise NotImplementedError(msg)

    def execute_details_type(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ItemT],
    ):
        """
        Executes the detailed executor for child executor
        """
        msg = f"{self.__class__.__name__} has not implemented execute_details_type"
        self.logging(msg)
        raise NotImplementedError(msg)

    def add_next_item(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[ItemT],
    ) -> None:
        """
        Adds the next item
        """
        msg = f"{self.__class__.__name__} has not implemented add_next_item"
        self.logging(msg)
        raise NotImplementedError(msg)
