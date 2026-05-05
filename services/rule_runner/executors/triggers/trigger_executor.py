from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...interfaces import BrowserPort


from time import sleep
import threading
from selenium.webdriver.common.by import By

from base import ErrorWrappers

from .trigger_action_based_executor import TriggerActionBasedExectuor


class TriggerExecutor:
    """
    Worker class responsible for handling trigger actions within rules, particularly
    setting frequency-based triggers using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        rule (dict): The rule data containing trigger information.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        rule (dict): The rule data containing trigger information.
    """

    def __init__(self, browser_port: BrowserPort, rule: dict, logger):
        """
        Initializes the TriggerWorker with the provided driver and rule data.
        Sets up the necessary connections for interacting with web elements.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rule (dict): The rule data containing trigger information.
        """
        super().__init__()
        self.browser_port = browser_port
        self.rule = rule
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
        Executes the trigger action by checking if the rule is frequency-based.
        If it is, sets the frequency-based trigger. Emits the finished signal when complete.
        """
        self.log_thread()
        if "frequency_based" in self.rule:

            self.set_frequency_based()

        if "action_based" in self.rule:
            self.set_action_based()

    def set_frequency_based(self) -> None:
        """
        Sets the frequency-based time interval for the rule.
        """
        self.logging("Setting rule frequency time interval...", "INFO")
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_Arrow")]',
        )

        # Set Frequency Rule Time ->>
        user_time_selection = str(self.rule["frequency_based"]["time_interval"])

        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
            user_time_selection,
        )

        sleep(1)

    def set_action_based(self) -> None:
        """
        Sets the action based trigger for the rule.
        """
        self.logging("Setting rule frequency time interval...", "INFO")

        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_lblAddEventSetFrequency")]',
        )

        executor = TriggerActionBasedExectuor(self.browser_port, self.rule, self.logger)
        executor.execute()
