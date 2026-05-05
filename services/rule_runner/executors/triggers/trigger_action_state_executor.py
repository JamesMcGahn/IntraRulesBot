from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...interfaces import BrowserPort

from time import sleep
import threading
from selenium.webdriver.common.by import By

from base import ErrorWrappers


class TriggerActionStateExecutor:
    """
    Worker class responsible for handling stats-based conditions within rules.
    This worker interacts with the UI to set the equality operator, threshold, and queue sources
    for stats-based conditions using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        condition (dict): The condition data that contains details such as equality operator and threshold.
        index (int): The index of the current condition in the list of conditions.
        conditions_worker (ConditionsWorker): The parent worker managing the conditions.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        _rule_condition_queues_source (str): The source of the rule condition, initially set to "queues".

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        conditions_worker (ConditionsWorker): The parent worker managing the conditions.
        condition (dict): The stats-based condition data.
        index (int): The index of the current condition.
    """

    def __init__(self, browser_port: BrowserPort, action_based: dict, logger):
        """
        Initializes the TriggerActionStateWorker with the provided driver, condition, index, and conditions_worker.
        Connects logging to web element interactions and sets up internal references for stats-based condition processing.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            action_based (dict): The stats-based action_based data.
            index (int): The index of the current condition.
        """
        super().__init__()
        self.browser_port = browser_port
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

    @ErrorWrappers.qworker_web_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to process the stats-based condition, including setting the equality operator,
        threshold, and queue sources. Emits the finished signal when complete.

        Returns:
            None: This function does not return a value.
        """
        self.log_thread()

        self.set_agent_and_aux()
        self.set_equality_operator()
        self.set_user_list()

    def set_state_changed_to(self, state):
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateSelectValue_Arrow")]',
        )
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateSelectValue_DropDown")]/div/ul/li',
            state,
        )

    def set_agent_aux(self, aux) -> None:
        """
        Sets the the aux code for the state changed to.

        Args:
            aux (str): the aux code.

        Returns:
            None: This function does not return a value.
        """
        self.browser_port.wait_and_type(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_agentStateAuxCodeValue")]',
            aux,
        )

    def set_agent_and_aux(self) -> None:
        """
        Sets the agent state and aux code for the state changed to for the array of state.

        Returns:
            None: This function does not return a value.
        """
        for agent_changed in self.action_based["details"]["state"]:
            self.set_state_changed_to(agent_changed["code"])
            self.set_agent_aux(agent_changed["aux"])

            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_divParameters")]/div[1]/div[1]/div[3]/img',
            )
            sleep(1)

    def set_equality_operator(self) -> None:
        """
        Sets the the equality operator for the state changed to.

        Returns:
            None: This function does not return a value.
        """
        user_selected_equality_op = self.action_based["details"]["equality_operator"]

        self.logging(
            f"Setting equality operator to {user_selected_equality_op}.", "INFO"
        )
        if user_selected_equality_op == "Equal To":
            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_ctl16_0")]',
            )

        elif user_selected_equality_op == "Not Equal To":
            self.browser_port.wait_and_click(
                By.XPATH,
                '//*[contains(@id, "overlayContent_triggerParameters_ctl16_1")]',
            )

    def set_user_list(self) -> None:
        """
        Sets the user list for the state changed to rule.

        Returns:
            None: This function does not return a value.
        """
        user_list_selection = self.action_based["details"]["user_list"]

        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "user_filter_static_id_Arrow")]',
        )
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "user_filter_static_id_DropDown")]/div/ul/li',
            user_list_selection,
        )
