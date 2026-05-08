from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...interfaces import BrowserPort
    from ....rules.models import Rule
    from ....rules.models.actions import Action
    from ....logger.adapters import LogAdapter

from time import sleep
import threading

from selenium.webdriver.common.by import By

from ..wrappers import ExecutorWrappers

from .actions_email_executor import ActionsEmailExecutor
from ....rules.enums import ACTIONDETAILTYPE


class ActionsExecutor:
    """
    Worker class responsible for handling multiple actions within rules.
    This worker interacts with the UI to set up Action's provider categories, instances,
    conditions, and email actions using Selenium WebDriver.
    """

    def __init__(
        self,
        browser_port: BrowserPort,
        rule: Rule,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        super().__init__()
        self.browser_port = browser_port
        self.rule = rule
        self.logger = logger
        self.should_stop = should_stop
        self.action_type_reg = {ACTIONDETAILTYPE.EMAIL: ActionsEmailExecutor}

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process each action within the rule, including setting
        provider categories, instances, conditions, and executing email actions. Emits the
        finished signal when the work is complete.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        for i, action in enumerate(self.rule.actions):

            self.set_provider_category(action, i)
            self.set_provider_instance(action, i)
            self.set_provider_condition(action, i)
            self.execute_details_type(action.details.action_type, self.rule, i)
            self.add_additional_action(i)

    def set_provider_category(self, action: Action, index: int) -> None:
        """
        Selects the provider category for the specified action.
        """
        self.logging(f"Selecting provider category for Action {index+1}...", "INFO")
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectAction_radMenuCategory")]/ul/li',
            action.provider_category,
            retries=5,
        )
        sleep(1)

    def set_provider_instance(self, action: Action, index: int) -> None:
        """
        Selects the provider instance for the specified action.
        """
        self.logging(f"Selecting provider instance for Action {index+1}...", "INFO")

        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuProviderInstance")]/ul/li',
            action.provider_instance,
            retries=5,
        )
        sleep(1)

    def set_provider_condition(self, action: Action, index: int) -> None:
        """
        Selects the provider condition for the specified action.
        """
        self.logging(f"Selecting condition selection for Action {index+1}...", "INFO")
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuItem")]/ul/li',
            action.provider_condition,
            retries=5,
        )

    def execute_details_type(
        self, action_type: ACTIONDETAILTYPE, rule: Rule, index: int
    ):
        executor = self.action_type_reg.get(action_type)
        if not executor:
            msg = f"{action_type} is not a supported trigger action"
            self.logging(msg, "ERROR")
            raise ValueError(msg)

        executor(
            self.browser_port, rule, index, self.logger, self.should_stop
        ).execute()

    def add_additional_action(self, index: int) -> None:
        """
        Adds additional actions to the UI if more than one action exists.
        """
        if index != len(self.rule.actions) - 1 and len(self.rule.actions) > 1:
            self.logging(f"Adding condition {index+2}...", "INFO")
            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_lblAddAction")]',
            )
            sleep(1)
