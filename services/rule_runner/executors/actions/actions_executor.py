from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...interfaces import BrowserPort

from time import sleep
import threading

from selenium.webdriver.common.by import By

from base import ErrorWrappers

from .actions_email_executor import ActionsEmailExecutor


class ActionsExecutor:
    """
    Worker class responsible for handling multiple actions within rules.
    This worker interacts with the UI to set up Action's provider categories, instances,
    conditions, and email actions using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        rule (dict): The rule data that contains the list of actions.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        _rule_condition_queues_source (str): The source of the rule condition, initially set to "queues".

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        rule (dict): The rule data used to configure the actions.
    """

    def __init__(self, browser_port: BrowserPort, rule: dict, logger):
        """
        Initializes the ActionsWorker with the provided driver and rule data.
        Sets up the necessary connections for interacting with web elements.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rule (dict): The rule data used to configure the actions.
        """
        super().__init__()
        self.browser_port = browser_port
        self.rule = rule
        self._rule_condition_queues_source = "queues"
        self.logger = logger

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        """
        Emit a log message.

        Args:
            msg (str): The message to log.
            level (str): The log level (e.g., "INFO","WARN", "ERROR"). Defaults to "INFO".
            print_msg (bool): Whether to print the message. Defaults to True.
        """
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger.insert(msg, level, print_msg)

    def log_thread(self) -> None:
        """
        Log the thread information for the worker.

        Logs the name of the current class and the thread identifier.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )

    @property
    def rule_condition_queues_source(self) -> str:
        """
        Gets the source of the rule condition (either "users" or "queues").

        Returns:
            str: The current rule condition queues source.
        """
        return self._rule_condition_queues_source

    @rule_condition_queues_source.setter
    def rule_condition_queues_source(self, source):
        """
        Sets the source of the rule condition (either "users" or "queues").

        Args:
            source (str): The new rule condition source.

        Returns:
            None: This function does not return a value.
        """
        self._rule_condition_queues_source = source

    @ErrorWrappers.qworker_web_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process each action within the rule, including setting
        provider categories, instances, conditions, and executing email actions. Emits the
        finished signal when the work is complete.

        Returns:
            None: This function does not return a value.
        """
        self.log_thread()
        for i, action in enumerate(self.rule["actions"]):

            self.set_provider_category(action, i)
            self.set_provider_instance(action, i)
            self.set_provider_condition(action, i)
            self.set_email_action(action, self.rule, i)
            self.add_additional_action(i)

    def set_provider_category(self, action: dict, i: int) -> None:
        """
        Selects the provider category for the specified action.

        Args:
            action (dict): The action data containing the provider category.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Selecting provider category for Action {i+1}...", "INFO")
        user_action_category_selection = action["provider_category"]
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_selectAction_radMenuCategory")]/ul/li',
            user_action_category_selection,
            retries=5,
        )
        sleep(1)

    def set_provider_instance(self, action: dict, i: int) -> None:
        """
        Selects the provider instance for the specified action.

        Args:
            action (dict): The action data containing the provider instance.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Selecting provider instance for Action {i+1}...", "INFO")
        user_action_provider_instance = action["provider_instance"]

        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuProviderInstance")]/ul/li',
            user_action_provider_instance,
            retries=5,
        )
        sleep(1)

    def set_provider_condition(self, action: dict, i: int) -> None:
        """
        Selects the provider condition for the specified action.

        Args:
            action (dict): The action data containing the provider condition.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Selecting condition selection for Action {i+1}...", "INFO")
        user_action_selection = action["provider_condition"]
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuItem")]/ul/li',
            user_action_selection,
            retries=5,
        )

    def set_email_action(self, action: dict, rule: dict, i: int) -> None:
        """
        Executes the email action for the specified action if the action type is email.

        Args:
            action (dict): The action data.
            rule (dict): The rule data.
            i (int): The index of the action in the list.

        Returns:
            None: This function does not return a value.
        """
        if action["details"]["action_type"] == "email":
            executor = ActionsEmailExecutor(
                self.browser_port, self, action, rule, i, self.logger
            )
            executor.execute()

    def add_additional_action(self, index: int) -> None:
        """
        Adds additional actions to the UI if more than one action exists.

        Args:
            index (int): The index of the current action.

        Returns:
            None: This function does not return a value.
        """
        if index != len(self.rule["actions"]) - 1 and len(self.rule["actions"]) > 1:
            self.logging(f"Adding condition {index+2}...", "INFO")
            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_lblAddAction")]',
            )
            sleep(1)
