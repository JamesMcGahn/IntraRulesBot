from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...interfaces import BrowserPort


from selenium.webdriver.common.by import By
import threading
from base import ErrorWrappers


class ConditionsStatsExecutor:
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

    def __init__(
        self,
        browser_port: BrowserPort,
        conditions_worker,
        condition: dict,
        index: int,
        logger,
    ):
        """
        Initializes the ConditionsStatsWorker with the provided driver, condition, index, and conditions_worker.
        Connects logging to web element interactions and sets up internal references for stats-based condition processing.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            conditions_worker (ConditionsWorker): The parent worker managing the conditions.
            condition (dict): The stats-based condition data.
            index (int): The index of the current condition.
        """
        super().__init__()
        self.browser_port = browser_port
        self.condition = condition
        self.index = index
        self.conditions_worker = conditions_worker
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
        condition_details = self.condition["details"]

        # equality comparison dropdown
        self.set_equality_operator(condition_details)
        self.set_equality_threshold(condition_details)
        # Condition numeric value input to compare

        user_condition_queues = condition_details["queues_source"]
        if user_condition_queues == "users":
            self.set_queues_sources_users()

        elif user_condition_queues == "queues":
            self.set_queues_sources_queue()

    def set_equality_operator(self, condition_details: dict) -> None:
        """
        Sets the equality operator for the stats-based condition.

        Args:
            condition_details (dict): The condition details containing the equality operator.

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting stats equality comparison operator for Condition {self.index+1}...",
            "INFO",
        )
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_Arrow")]',
        )

        # equality comparison operator selection
        user_agents_in_after_call_eq = condition_details["equality_operator"]

        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_DropDown")]/div/ul/li',
            user_agents_in_after_call_eq,
        )

    def set_equality_threshold(self, condition_details: dict) -> None:
        """
        Sets the equality threshold for the stats-based condition.

        Args:
            condition_details (dict): The condition details containing the equality threshold.

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting stats threshold for Condition {self.index+1}...",
            "INFO",
        )
        user_agents_in_after_call_eq_condition = condition_details["equality_threshold"]
        self.browser_port.wait_and_type(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_tbExposedDataValue")]',
            user_agents_in_after_call_eq_condition,
        )

    def set_queues_sources_users(self) -> None:
        """
        Sets the queue source for the condition to "users".

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting queue source as 'users' for Condition {self.index+1}...",
            "INFO",
        )
        self.conditions_worker.rule_condition_queues_source = "users"

    def set_queues_sources_queue(self) -> None:
        """
        Sets the queue source for the condition to "queues" and selects all queues.

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Selecting queue source as 'queues' for Condition {self.index+1}...",
            "INFO",
        )
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl16_1")]',
        )

        self.logging(
            f"Selecting queue all listed queues for Condition {self.index+1}...",
            "INFO",
        )
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl22_Arrow")]',
        )

        self.browser_port.click_all_items_in_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_conditionParameters_ctl22_DropDown")]/div/ul/li',
            retries=5,
            item_name="queues in queues list",
        )
