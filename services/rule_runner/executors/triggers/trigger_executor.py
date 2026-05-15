from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ....browser.ports import FramePort
    from ....rules.models import Rule
    from ....logger.adapters import LogAdapter


from ....rules.models.triggers import FrequencyTrigger, ActionTrigger
import threading

from ..wrappers import ExecutorWrappers

from .trigger_action_based_executor import TriggerActionBasedExectuor


class TriggerExecutor:
    """
    Worker class responsible for handling trigger actions within rules, particularly
    setting frequency-based triggers using Selenium WebDriver.
    """

    def __init__(
        self,
        frame_port: FramePort,
        rule: Rule,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        super().__init__()
        self.frame_port = frame_port
        self.rule = rule
        self.logger = logger
        self.should_stop = should_stop

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the trigger action by checking if the rule is trigger type.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        if self.should_stop():
            return
        if isinstance(self.rule.trigger, FrequencyTrigger):
            self.execute_frequency_trigger()
        elif isinstance(self.rule.trigger, ActionTrigger):
            TriggerActionBasedExectuor(
                self.frame_port, self.rule, self.logger, self.should_stop
            ).execute()
        else:
            msg = f"Trigger type {self.rule.trigger.__class__.__name__} is unsupported"
            self.logging(msg, "ERROR")
            raise ValueError(msg)

    def execute_frequency_trigger(self) -> None:
        """
        Sets the frequency-based time interval for the rule.
        """
        self.logging("Setting rule frequency time interval...", "INFO")
        self.frame_port.click(
            '[id*="overlayContent_triggerParameters_frequencyComboBox_Arrow"]'
        )

        # Set Frequency Rule Time ->>
        user_time_selection = str(self.rule.trigger.time_interval)
        self.frame_port.select_exact_item_from_list(
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
            user_time_selection,
        )
