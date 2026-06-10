from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState
import threading
from ..wrappers import ExecutorWrappers
from ...enums import EXECUTORSCOPE, EXECUTORTASK
from ...models import EXECSTEPCALL
from ..base import BaseScopeExecutor


class BaseScopeChildExecutor(BaseScopeExecutor):
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
        ]
        self._detail_type_registry = None

    @property
    def detail_type_registry(self) -> dict:

        if self._detail_type_registry is None:

            raise RuntimeError("Detail type registry has not been initialized")

        return self._detail_type_registry

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

        for step in self._flow:
            self.run_step(step)

    def set_provider_category(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Selects the provider category.
        """
        msg = f"{self.__class__.__name__} has not implemented set_provider_category"
        self.logging(msg)
        raise NotImplementedError(msg)

    def set_provider_instance(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Selects the provider instance.
        """
        msg = f"{self.__class__.__name__} has not implemented set_provider_instance"
        self.logging(msg)
        raise NotImplementedError(msg)

    def set_provider_condition(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Selects the provider condition.
        """
        msg = f"{self.__class__.__name__} has not implemented set_provider_condition"
        self.logging(msg)
        raise NotImplementedError(msg)

    def execute_details_type(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ):
        """
        Executes the detailed executor for child executor
        """
        msg = f"{self.__class__.__name__} has not implemented execute_details_type"
        self.logging(msg)
        raise NotImplementedError(msg)
