from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext
    from ....browser.ports import InteractionPort

from ...enums import EXECUTORSCOPE, EXECUTORTASK, RULEEXECSTATUS
from base.errors import StoppedRequestException
from ...models import (
    EXECSTEPCALL,
    ExecutorTaskRef,
    RuleExecutionResult,
    RuleExecutionState,
    RuleProgressEvent,
)


class BaseScopeExecutor:
    """
    Worker class responsible for creating rules in a web application using Selenium WebDriver.
    It handles setting up the rule name, triggers, conditions, and actions, and submitting the rule form.
    Handles exceptions such as duplicate rule names and WebDriver issues.
    """

    def __init__(
        self,
        scope_id: EXECUTORSCOPE,
        rule_context: RuleExecutionContext,
        state: RuleExecutionState,
    ):
        self._ctx = rule_context
        self._scope_id = scope_id
        self._state = state

    @property
    def form_port(self) -> InteractionPort:

        if self._state.interaction_port is None:

            raise RuntimeError("Rule form interaction port has not been initialized.")

        return self._state.interaction_port

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self._ctx.logger(msg, level, print_msg)

    def task_ref(
        self,
        task: EXECUTORTASK,
        index: int | None = None,
        detail_type: str | None = None,
    ) -> ExecutorTaskRef:

        return ExecutorTaskRef(
            scope=self._scope_id,
            task=task,
            index=index,
            detail_type=detail_type,
        )

    def rule_progress(self, message=None):
        self._ctx.progress_cb(
            RuleProgressEvent(
                rule_guid=self._ctx.rule.guid,
                rule_name=self._state.rule_name,
                task_ref=self._state.current_task,
                status=self._state.status,
                message=message,
            )
        )

    def set_state_status(self, task_ref: ExecutorTaskRef, status: RULEEXECSTATUS):
        self._state.current_task = task_ref
        self._state.status = status
        self.rule_progress()

    def run_step(self, step: EXECSTEPCALL):

        ref = self.task_ref(step.task)
        self.set_state_status(ref, RULEEXECSTATUS.RUNNING)
        if self._ctx.should_stop():
            raise StoppedRequestException("Stop Requested")
        try:
            handler = step.handler
            handler(self._ctx, self._state)
        except Exception as e:
            print(e)

            if self._ctx.should_stop():
                self.set_state_status(ref, RULEEXECSTATUS.RUNNER_STOPPED_ERROR)
                raise StoppedRequestException("Stop Requested") from e

            self.set_state_status(ref, RULEEXECSTATUS.UNKNOWN_ERROR)
            raise
        self.set_state_status(ref, RULEEXECSTATUS.SUCCESS)

    def execute(self) -> RuleExecutionResult:
        """
        Executes the rule creation process by navigating through the form pages, setting up triggers, conditions,
        and actions, and submitting the rule. Handles duplicate rule names and retries.
        """
        msg = "execute is not implemented."
        self.logging(msg, "ERROR")
        raise NotImplementedError(msg)

    def _build_error_result(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        status: RULEEXECSTATUS,
        message: str,
    ):
        self.logging(message, "ERROR")
        return RuleExecutionResult(
            rule_guid=ctx.rule.guid,
            rule_name=state.rule_name,
            task_ref=state.current_task,
            success=False,
            status=status,
            message=message,
        )
