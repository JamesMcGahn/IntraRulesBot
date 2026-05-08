from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...interfaces import BrowserPort
    from ....rules.models import Rule
    from ....rules.models.triggers import ActionTrigger
    from ....logger.adapters import LogAdapter

from time import sleep
import threading
from selenium.webdriver.common.by import By

from ..wrappers import ExecutorWrappers

from .trigger_action_state_changed_executor import TriggerActionStateChangedExecutor
from ....rules.enums import ACTIONTRIGGERDETAILTYPE


class TriggerActionBasedExectuor:
    """
    Worker class responsible for handling Action Based Triggers within rules.
    This worker interacts with the UI to set up Action Based Triggers's provider categories, instances,
    conditions, and email actions using Selenium WebDriver.
    """

    def __init__(
        self,
        browser_port: BrowserPort,
        rule: Rule,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        """
        Initializes the ActionsWorker with the provided driver and rule data.
        Sets up the necessary connections for interacting with web elements.
        """
        super().__init__()
        self.browser_port = browser_port
        self.rule = rule
        self._rule_condition_queues_source = "queues"
        self.logger = logger
        self.should_stop = should_stop
        self.action_type_reg = {
            ACTIONTRIGGERDETAILTYPE: TriggerActionStateChangedExecutor
        }

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process each Action Based Trigger within the rule, including setting
        provider categories, instances, conditions, and executing email actions. Emits the
        finished signal when the work is complete.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        self.logging("Choosing Trigger Event", "INFO")
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_lblAddEventSetFrequency")]',
        )
        action_based = self.rule.trigger
        self.set_provider_category(action_based)
        self.set_provider_instance(action_based)
        self.set_provider_condition(action_based)
        self.set_action_state(action_based)

        self.execute_details_type(self.rule.trigger.details.action_type, self.rule)

    def set_provider_category(self, action_trigger: ActionTrigger) -> None:
        """
        Selects the provider category for the specified action.
        """
        self.logging("Selecting provider category for Action Trigger", "INFO")

        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectTrigger_radMenuCategory")]/ul/li',
            action_trigger.provider_category,
        )
        sleep(1)

    def set_provider_instance(self, action_trigger: ActionTrigger) -> None:
        """
        Selects the provider instance for the specified condition.
        """
        self.logging("Selecting provider instance for Action Trigger", "INFO")
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectTrigger_radMenuProviderInstance")]/ul/li',
            action_trigger.provider_instance,
        )

        sleep(1)

    def set_provider_condition(self, action_trigger: ActionTrigger) -> None:
        """
        Selects the provider condition for the specified condition.
        """
        self.logging("Selecting condition selection for Action Trigger", "INFO")

        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectTrigger_radMenuItem")]/ul/li',
            action_trigger.provider_condition,
            5,
        )

        sleep(1)

    def execute_details_type(self, action_type: ACTIONTRIGGERDETAILTYPE, rule: Rule):
        executor = self.action_type_reg.get(action_type)
        if not executor:
            msg = f"{action_type} is not a supported trigger action"
            self.logging(msg, "ERROR")
            raise ValueError(msg)

        executor(self.browser_port, rule, self.logger, self.should_stop).execute()
