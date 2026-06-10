from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, Callable

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState

import threading
from ..base import BaseScopeExecutor
from ..wrappers import ExecutorWrappers
from ...enums import EXECUTORSCOPE
from ...models.executor_item_context import ExecutorItemContext

SelectorsT = TypeVar("SelectorsT")
ItemT = TypeVar("ItemT")


class BaseChildDetailedExecutor(BaseScopeExecutor, Generic[ItemT, SelectorsT]):

    def __init__(
        self,
        scope_id: EXECUTORSCOPE,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: SelectorsT,
        item_context: ExecutorItemContext[ItemT],
    ):
        super().__init__(scope_id, context, state)

        self._flow = None
        self._selectors = selectors
        self._item_ctx = item_context

    @property
    def flow(self) -> list[Callable]:
        if self._flow is None:
            raise RuntimeError("Flow steps have not been initialized")

        return self._flow

    @property
    def selectors(self) -> SelectorsT:
        if self._selectors is None:
            raise RuntimeError("selectors have not been initialized")

        return self._selectors

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process the scope's child detail actions.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )

        for step in self.flow:
            step(self._ctx, self._state, self._item_ctx)
