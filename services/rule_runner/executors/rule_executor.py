from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interfaces import BrowserPort

from time import sleep
import threading
from selenium.common.exceptions import (
    NoSuchFrameException,
    WebDriverException,
)
from selenium.webdriver.common.by import By

from base.exceptions import DuplicateRuleName

from .actions import ActionsExecutor
from .conditions import ConditionsExecutor
from .triggers import TriggerExecutor


class RuleExecutor:
    """
    Worker class responsible for creating rules in a web application using Selenium WebDriver.
    It handles setting up the rule name, triggers, conditions, and actions, and submitting the rule form.
    Handles exceptions such as duplicate rule names and WebDriver issues.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        rule (dict): The rule data that contains trigger, condition, and action information.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        rule_rename_attempts (int): Tracks the number of rename attempts in case of duplicate rule names.
        rule_name (str): The name of the rule being processed.

    Signals:
        finished (Signal[str]): Emitted when the rule is successfully created.
        error (Signal[bool]): Emitted when an error occurs during rule creation.
    """

    def __init__(self, browser_port: BrowserPort, rule: dict, logger):
        """
        Initializes the RuleWorker with the provided WebDriver instance and rule data.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rule (dict): The rule data that contains trigger, condition, and action information.
        """
        super().__init__()
        self.browser_port = browser_port
        self.rule = rule
        self.logger = logger

        self.rule_rename_attempts = 0
        self.rule_name = rule["rule_name"]

        self.stop_rule_worker = False

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

    def execute(self) -> None:
        """
        Executes the rule creation process by navigating through the form pages, setting up triggers, conditions,
        and actions, and submitting the rule. Handles duplicate rule names and retries.

        Returns:
            None: This function does not return a value.
        """
        try:
            self.logging(
                f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
                "INFO",
            )
            self.browser_port.wait_and_click(
                By.ID,
                "ctl00_ActionBarContent_rbAction_Add",
            )
            self.switch_to_rule_module()

            if self.is_tutorial_page_present():
                self.logging("Tutorial Page is present...", "INFO")
                self.next_page()

            self.set_rule_name(self.rule_name)
            self.start_trigger_page()
            if self.stop_rule_worker:
                return

            self.next_page()

            self.start_conditions_page()
            if self.stop_rule_worker:
                return

            self.next_page()

            self.start_actions_page()
            if self.stop_rule_worker:
                return

            self.set_rule_category()
            if self.stop_rule_worker:
                return

            self.switch_to_rule_module()
            self.next_page()
            if self.stop_rule_worker:
                return

            self.submit_rule()
            if self.stop_rule_worker:
                return

            if self.rule_rename_attempts == 0:
                return self.rule["guid"]
            else:
                old_rule_name = self.rule["rule_name"]
                self.logging(f"{old_rule_name} renamed {self.rule_name}")
                return self.rule["guid"]
        except DuplicateRuleName:
            return None

        except NoSuchFrameException:
            self.logging("Can't Find Frame. The window was closed.", "ERROR")
            return None
        except WebDriverException as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            return None
        except Exception as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            return None

    def start_trigger_page(self) -> None:
        """
        Starts processing the triggers for the rule by initializing the TriggerWorker.

        Returns:
            None: This function does not return a value.
        """
        self.trigger = TriggerExecutor(self.browser_port, self.rule, self.logger)
        self.trigger.execute()

    def start_conditions_page(self) -> None:
        """
        Starts processing the conditions for the rule by initializing the ConditionsWorker.

        Returns:
            None: This function does not return a value.
        """

        if "conditions" in self.rule and self.rule["conditions"]:
            self.conditions = ConditionsExecutor(
                self.browser_port, self.rule, self.logger
            )
            self.conditions.execute()

    def start_actions_page(self) -> None:
        """
        Starts processing the actions for the rule by initializing the ActionsWorker.

        Returns:
            None: This function does not return a value.
        """

        if "actions" in self.rule and self.rule["actions"]:
            executor = ActionsExecutor(self.browser_port, self.rule, self.logger)
            # TODO remove this dependacy
            executor.rule_condition_queues_source = (
                self.conditions.rule_condition_queues_source
            )

            executor.execute()

    def switch_to_rule_module(self) -> None:
        """
        Switches the WebDriver to the rule modal frame to interact with rule elements.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Switching to the Rule Modal...", "INFO")
        self.browser_port.switch_to_frame(By.NAME, "RadWindowAddEditRule")

    def set_rule_name(self, rule_name: str) -> None:
        """
        Sets the rule name in the rule creation form.

        Args:
            rule_name (str): The name of the rule to be set.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Setting the Rule Name...", "INFO")
        self.browser_port.wait_and_type(
            By.XPATH,
            '//*[contains(@id, "overlayRuleProgressArea_tbRuleName")]',
            rule_name,
        )

    def next_page(self) -> None:
        """
        Navigates to the next page in the rule creation form.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Navigating to the Next Page...", "INFO")
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            wait_time=35,
        )

    def is_tutorial_page_present(self) -> bool:
        """
        Checks if the tutorial page is present and can be skipped.

        Returns:
            bool: True if the tutorial page is present, False otherwise.
        """
        return self.browser_port.wait_for_element(
            By.XPATH,
            '//*[contains(@id, "overlayButtonsLeft_cbDontAskLead")]',
            wait_time=5,
            retries=1,
            raise_exception=False,
        )

    def submit_rule(self) -> None:
        """
        Submits the rule form, handling duplicate rule alerts by renaming the rule and retrying.

        Returns:
            None: This function does not return a value.
        """

        self.logging(f"Submitting Rule - {self.rule_name }...", "INFO")

        def handle_duplicate_alert():
            for _ in range(2):

                # Retry twice before giving up
                alert = self.wait_for_dup_rule_alert(10)
                if alert:
                    self.rename_rule()
                    self.logging(
                        f"Retrying Rule Submission for renamed rule - {self.rule_name }...",
                        "INFO",
                    )
                    self.browser_port.wait_and_click(
                        By.XPATH,
                        '//*[contains(@id, "overlayButtons_rbSubmit_input")]',
                        15,
                    )
                else:
                    return False  # No alert found, submission is successful
            return True

        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbSubmit_input")]',
            15,
        )
        if handle_duplicate_alert():
            if self.wait_for_dup_rule_alert(5):
                self.logging(
                    f"Rule '{self.rule_name}' could not be submitted after multiple retries.",
                    "ERROR",
                )
                raise DuplicateRuleName

        self.browser_port.switch_to_main_frame()
        self.success_message()

    def rename_rule(self) -> None:
        """
        Renames the rule in case of a duplicate name error.

        Returns:
            None: This function does not return a value.
        """
        self.rule_rename_attempts += 1
        old_rule_name = self.rule["rule_name"]
        self.rule_name = f"{old_rule_name}-{self.rule_rename_attempts}"
        self.logging(
            f"Trying to rename rule: {old_rule_name} as {self.rule_name}",
            "ERROR",
        )
        self.set_rule_name(self.rule_name)

    def success_message(self) -> None:
        """
        Logs a success message after the rule has been successfully created.

        Returns:
            None: This function does not return a value.
        """
        self.browser_port.wait_for_element(
            By.ID,
            "ctl00_ActionBarContent_rbAction_Add",
            raise_exception=True,
        )
        self.logging(f"Rule: {self.rule_name} has been created.", "INFO")

    def set_rule_category(self) -> None:
        """
        Sets the rule category in the rule creation form.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Setting the rule category", "INFO")
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_divAddEditAction")]/div[3]/a',
        )
        sleep(1)
        self.browser_port.switch_to_main_frame()
        self.browser_port.switch_to_frame(By.NAME, "RadWindowAddEditRuleSettings")
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_Arrow")]',
        )
        self.browser_port.select_item_from_list(
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
            self.rule["rule_category"],
        )

        sleep(1)
        self.logging("Switching the main frame", "INFO")
        self.browser_port.switch_to_main_frame()

    def wait_for_dup_rule_alert(self, wait_time: int) -> bool:
        """
        Waits for a duplicate rule alert and handles it by accepting the alert.

        Args:
            wait_time (int): The time (in seconds) to wait for the alert.

        Returns:
            bool: True if the alert is found and accepted, False otherwise.
        """
        alert_present = self.browser_port.wait_and_accept_alert(
            "A Rule with this name already exists", wait_time
        )
        if alert_present:
            self.logging(
                f"A Rule with the name {self.rule_name} already exists.", "ERROR"
            )
            self.logging(
                "Accepting window alert notifying of duplicate rule name.", "INFO"
            )
            return True
        else:
            self.logging(f"Rule: {self.rule_name} has been submitted.", "INFO")
            return False

    def handle_child_error(self, msg):
        self.stop_rule_worker = True
        return
