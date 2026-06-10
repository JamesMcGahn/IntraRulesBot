from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from ...models import RuleExecutionContext, RuleExecutionState
    from ..base import BaseScopeExecutor
from ....rules.models.triggers import FrequencyTrigger, ActionTrigger
import threading

from ..wrappers import ExecutorWrappers
from ..base import BaseScopeExecutor
from .trigger_action_based_executor import TriggerActionBasedExectuor
from ...enums import EXECUTORSCOPE, EXECUTORTASK
from ...models import EXECSTEPCALL


class TriggerExecutor(BaseScopeExecutor):
    """
    Executor class responsible for handling trigger actions within rules
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
    ):
        super().__init__(EXECUTORSCOPE.TRIGGER, context, state)

        self._triggers = {
            FrequencyTrigger: EXECSTEPCALL(
                EXECUTORTASK.START, self.execute_frequency_trigger
            ),
            ActionTrigger: EXECSTEPCALL(
                EXECUTORTASK.START, self.execute_action_based_trigger
            ),
        }

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the trigger action by checking if the rule is trigger type.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        trigger_type = type(self._ctx.rule.trigger)
        trigger = self._triggers.get(trigger_type, None)
        if not trigger:
            raise NotImplementedError(f"{trigger_type} has not been implemented")

        self.run_step(trigger)

    def execute_action_based_trigger(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:

        self.logging("Choosing Trigger Event", "INFO")
        self.form_port.click(
            ctx.profile.selectors.triggers.common.add_event_trigger_button
        )

        TriggerActionBasedExectuor(ctx, state).execute()

    def execute_frequency_trigger(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Sets the frequency-based time interval for the rule.
        """
        self.logging("Setting rule frequency time interval...", "INFO")
        self.form_port.click(
            ctx.profile.selectors.triggers.common.frequency_dropdown_arrow
        )

        # Set Frequency Rule Time ->>
        user_time_selection = str(ctx.rule.trigger.time_interval)
        self.form_port.select_exact_item_from_list(
            ctx.profile.selectors.triggers.common.frequency_dropdown_list,
            user_time_selection,
        )
