from time import sleep

from PySide6.QtCore import Signal
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchFrameException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base import QWorkerBase
from base.exceptions import DuplicateRuleName

from .actions import ActionsWorker
from .conditions import ConditionsWorker
from .triggers import TriggerWorker
from .utils import WaitConditions, WebElementInteractions


class RuleWorker(QWorkerBase):
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

    finished = Signal(str)
    error = Signal(bool)

    def __init__(self, driver: webdriver.Chrome, rule: dict):
        """
        Initializes the RuleWorker with the provided WebDriver instance and rule data.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rule (dict): The rule data that contains trigger, condition, and action information.
        """
        super().__init__()
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self.wELI.send_msg.connect(self.logging)
        self.rule_rename_attempts = 0
        self.rule_name = rule["rule_name"]

    def do_work(self) -> None:
        """
        Executes the rule creation process by navigating through the form pages, setting up triggers, conditions,
        and actions, and submitting the rule. Handles duplicate rule names and retries.

        Returns:
            None: This function does not return a value.
        """
        try:
            self.log_thread()
            addRuleBtn = self.wELI.wait_for_element(
                20,
                By.ID,
                "ctl00_ActionBarContent_rbAction_Add",
                WaitConditions.CLICKABLE,
                raise_exception=True,
            )
            if addRuleBtn:
                addRuleBtn.click()

                self.switch_to_rule_module()

                if self.is_tutorial_page_present():
                    self.logging("Tutorial Page is present...", "INFO")
                    self.next_page()

                self.set_rule_name(self.rule_name)
                self.start_trigger_page()
                self.next_page()
                self.start_conditions_page()
                self.next_page()
                self.start_actions_page()
                self.set_rule_category()
                self.switch_to_rule_module()
                self.next_page()
                self.submit_rule()

                if self.rule_rename_attempts == 0:
                    self.finished.emit(self.rule_name)
                else:
                    old_rule_name = self.rule["rule_name"]
                    self.finished.emit(f"{old_rule_name} renamed {self.rule_name}")
        except DuplicateRuleName:
            self.error.emit(False)

        except NoSuchFrameException:
            self.logging("Can't Find Frame. The window was closed.", "ERROR")
            self.error.emit(True)
        except WebDriverException as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            self.error.emit(True)
        except Exception as e:
            self.logging(f"Something went wrong in RuleWorker: {e}", "ERROR")
            self.error.emit(True)

    def start_trigger_page(self) -> None:
        """
        Starts processing the triggers for the rule by initializing the TriggerWorker.

        Returns:
            None: This function does not return a value.
        """
        self.trigger = TriggerWorker(self.driver, self.rule)
        self.trigger.send_logs.connect(self.logging)
        self.trigger.finished.connect(self.trigger.deleteLater)
        self.trigger.do_work()

    def start_conditions_page(self) -> None:
        """
        Starts processing the conditions for the rule by initializing the ConditionsWorker.

        Returns:
            None: This function does not return a value.
        """
        self.conditions = ConditionsWorker(self.driver, self.rule)
        if "conditions" in self.rule and self.rule["conditions"]:
            self.conditions.send_logs.connect(self.logging)
            self.conditions.finished.connect(self.conditions.deleteLater)
            self.conditions.do_work()

    def start_actions_page(self) -> None:
        """
        Starts processing the actions for the rule by initializing the ActionsWorker.

        Returns:
            None: This function does not return a value.
        """
        self.actions = ActionsWorker(self.driver, self.rule)
        if "actions" in self.rule and self.rule["actions"]:
            self.actions.rule_condition_queues_source = (
                self.conditions.rule_condition_queues_source
            )
            self.actions.send_logs.connect(self.logging)
            self.actions.finished.connect(self.actions.deleteLater)
            self.actions.do_work()

    def switch_to_rule_module(self) -> None:
        """
        Switches the WebDriver to the rule modal frame to interact with rule elements.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Switching to the Rule Modal...", "INFO")
        self.wELI.switch_to_frame(20, By.NAME, "RadWindowAddEditRule")

    def set_rule_name(self, rule_name: str) -> None:
        """
        Sets the rule name in the rule creation form.

        Args:
            rule_name (str): The name of the rule to be set.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Setting the Rule Name...", "INFO")
        rule_name_input = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayRuleProgressArea_tbRuleName")]',
            WaitConditions.VISIBILITY,
        )
        rule_name_input.clear()
        rule_name_input.send_keys(rule_name)

    def next_page(self) -> None:
        """
        Navigates to the next page in the rule creation form.

        Returns:
            None: This function does not return a value.
        """
        self.logging("Navigating to the Next Page...", "INFO")
        continue_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            WaitConditions.CLICKABLE,
        )
        sleep(1)
        continue_btn.click()

    def is_tutorial_page_present(self) -> bool:
        """
        Checks if the tutorial page is present and can be skipped.

        Returns:
            bool: True if the tutorial page is present, False otherwise.
        """
        return self.wELI.wait_for_element(
            5,
            By.XPATH,
            '//*[contains(@id, "overlayButtonsLeft_cbDontAskLead")]',
            WaitConditions.CLICKABLE,
            raise_exception=False,
            retries=1
        )

    def submit_rule(self) -> None:
        """
        Submits the rule form, handling duplicate rule alerts by renaming the rule and retrying.

        Returns:
            None: This function does not return a value.
        """

        self.logging(f"Submitting Rule - {self.rule_name }...", "INFO")
        submit_btn = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbSubmit_input")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )

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
                    submit_btn.click()
                else:
                    return False  # No alert found, submission is successful
            return True

        submit_btn.click()

        if handle_duplicate_alert():
            if self.wait_for_dup_rule_alert(5):
                self.logging(
                    f"Rule '{self.rule_name}' could not be submitted after multiple retries.",
                    "ERROR",
                )
                raise DuplicateRuleName

        self.driver.switch_to.default_content()
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
        self.wELI.wait_for_element(
            20,
            By.ID,
            "ctl00_ActionBarContent_rbAction_Add",
            WaitConditions.CLICKABLE,
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
        rule_settings_hamburger = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "overlayContent_divAddEditAction")]/div[3]/a',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        rule_settings_hamburger.click()
        sleep(1)
        self.driver.switch_to.default_content()
        self.wELI.switch_to_frame(20, By.NAME, "RadWindowAddEditRuleSettings")
        rule_category_dropdown_arrow = self.wELI.wait_for_element(
            15,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_Arrow")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        rule_category_dropdown_arrow.click()
        rule_category_selection = self.rule["rule_category"]
        self.wELI.select_item_from_list(
            20,
            By.XPATH,
            '//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
            rule_category_selection,
            raise_exception=True,
        )
        sleep(1)
        self.logging("Switching the main frame", "INFO")
        self.driver.switch_to.default_content()

    def wait_for_dup_rule_alert(self, wait_time: int) -> bool:
        """
        Waits for a duplicate rule alert and handles it by accepting the alert.

        Args:
            wait_time (int): The time (in seconds) to wait for the alert.

        Returns:
            bool: True if the alert is found and accepted, False otherwise.
        """

        try:
            WebDriverWait(self.driver, wait_time).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            if "A Rule with this name already exists" in alert.text:

                self.logging(
                    f"A Rule with the name {self.rule_name} already exists.", "ERROR"
                )
                self.logging(
                    "Accepting window alert notifying of duplicate rule name.", "INFO"
                )
                alert.accept()

                if alert:
                    return True

        except TimeoutException:
            self.logging(f"Rule: {self.rule_name} has been submitted.", "INFO")
            return False
