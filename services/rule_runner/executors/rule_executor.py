from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...browser.ports import BrowserPort
    from ...rules.models import Rule
    from ...logger.adapters import LogAdapter
    from ...browser.ports import FramePort

import threading

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


from ..errors import (
    DuplicateRuleNameException,
    StoppedRequestException,
    PlaywrightSessionLostException,
)

from .actions import ActionsExecutor
from .conditions import ConditionsExecutor
from .triggers import TriggerExecutor
from ..models import RuleExecutionResult
from ..enums import RULEEXECSTATUS


class RuleExecutor:
    """
    Worker class responsible for creating rules in a web application using Selenium WebDriver.
    It handles setting up the rule name, triggers, conditions, and actions, and submitting the rule form.
    Handles exceptions such as duplicate rule names and WebDriver issues.
    """

    def __init__(
        self,
        url: str,
        browser_port: BrowserPort,
        rule: Rule,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        super().__init__()
        self.url = url
        self.browser_port = browser_port
        self.rule = rule
        self.logger = logger
        self.should_stop = should_stop
        self.rule_rename_attempts = 0
        self.rule_name = rule.rule_name

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def execute(self) -> RuleExecutionResult:
        """
        Executes the rule creation process by navigating through the form pages, setting up triggers, conditions,
        and actions, and submitting the rule. Handles duplicate rule names and retries.
        """
        try:
            self.logging(
                f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
                "INFO",
            )

            self.logging("Navigating to the Rules Page...", "INFO")
            self.browser_port.goto(self.url + "/ManagerConsole/Delivery/Rules.aspx")

            self.browser_port.click("#ctl00_ActionBarContent_rbAction_Add", 3000)
            frame_port = self.switch_to_rule_module()

            if self.is_tutorial_page_present(frame_port=frame_port):
                self.logging("Tutorial Page is present...", "INFO")
                self.next_page(frame_port=frame_port)

            self.set_rule_name(frame_port=frame_port, rule_name=self.rule_name)

            self.execute_triggers(frame_port=frame_port)
            if self.should_stop():
                return self._build_stopped_result()

            self.next_page(frame_port=frame_port)

            self.execute_conditions(frame_port=frame_port)
            if self.should_stop():
                return self._build_stopped_result()

            self.next_page(frame_port=frame_port)

            self.execute_actions(frame_port=frame_port)
            if self.should_stop():
                return self._build_stopped_result()

            self.set_rule_category(frame_port=frame_port)
            if self.should_stop():
                return self._build_stopped_result()

            # self.switch_to_rule_module()
            self.next_page(frame_port=frame_port)
            if self.should_stop():
                return self._build_stopped_result()

            self.submit_rule(frame_port=frame_port)
            if self.should_stop():
                return self._build_stopped_result()

            if self.rule_rename_attempts > 0:
                old_rule_name = self.rule.rule_name
                self.logging(f"{old_rule_name} renamed {self.rule_name}")

            return RuleExecutionResult(
                rule_guid=self.rule.guid,
                rule_name=self.rule_name,
                success=True,
                status=RULEEXECSTATUS.SUCCESS,
                message="Rule submitted successfully.",
            )
        except StoppedRequestException:
            return RuleExecutionResult(
                rule_guid=self.rule.guid,
                rule_name=self.rule.rule_name,
                success=False,
                status=RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
                message="Stopped Requested.",
            )

        except DuplicateRuleNameException:
            return RuleExecutionResult(
                rule_guid=self.rule.guid,
                rule_name=self.rule.rule_name,
                success=False,
                status=RULEEXECSTATUS.NAME_EXISTS_ERROR,
                message="Rule name still exists after 2 renaming tries.",
            )

        except PlaywrightSessionLostException:
            if self.should_stop():
                return RuleExecutionResult(
                    rule_guid=self.rule.guid,
                    rule_name=self.rule.rule_name,
                    success=False,
                    status=RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
                    message="Stopped Requested.",
                )

            self.logging(
                "Can't Find Frame. The window was closed. Rule Failed.", "ERROR"
            )
            return RuleExecutionResult(
                rule_guid=self.rule.guid,
                rule_name=self.rule.rule_name,
                success=False,
                status=RULEEXECSTATUS.BROWSER_ERROR,
                message="Browser doesnt exist.",
            )

        except PlaywrightTimeoutError:
            self.logging("Finding element timed out. Rule Failed.", "ERROR")
            return RuleExecutionResult(
                rule_guid=self.rule.guid,
                rule_name=self.rule.rule_name,
                success=False,
                status=RULEEXECSTATUS.TIMEOUT_ERROR,
                message="Element doesnt exist.",
            )

        except PlaywrightError as e:
            self.logging(
                f"Something went wrong in RuleWorker. Rule Failed.: {e}", "ERROR"
            )
            return RuleExecutionResult(
                rule_guid=self.rule.guid,
                rule_name=self.rule.rule_name,
                success=False,
                status=RULEEXECSTATUS.BROWSER_ERROR,
                message="Browser error.",
            )
        except Exception as e:
            if self.should_stop():
                return RuleExecutionResult(
                    rule_guid=self.rule.guid,
                    rule_name=self.rule.rule_name,
                    success=False,
                    status=RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
                    message="Stopped Requested.",
                )

            self.logging(
                f"Something went wrong in RuleWorker. Rule Failed.: {e}", "ERROR"
            )
            return RuleExecutionResult(
                rule_guid=self.rule.guid,
                rule_name=self.rule.rule_name,
                success=False,
                status=RULEEXECSTATUS.UNKNOWN_ERROR,
                message="Error happened in rule execution.",
            )

    def execute_triggers(self, frame_port: FramePort) -> None:
        """
        Starts processing the triggers for the rule by initializing the TriggerWorker.
        """
        self.trigger = TriggerExecutor(
            frame_port, self.rule, self.logger, self.should_stop
        )
        self.trigger.execute()

    def execute_conditions(self, frame_port: FramePort) -> None:
        """
        Starts processing the conditions for the rule by initializing the ConditionsWorker.
        """

        if self.rule.conditions:
            self.conditions = ConditionsExecutor(
                frame_port, self.rule, self.logger, self.should_stop
            )
            self.conditions.execute()

    def execute_actions(self, frame_port: FramePort) -> None:
        """
        Starts processing the actions for the rule by initializing the ActionsWorker.
        """

        if self.rule.actions:
            executor = ActionsExecutor(
                frame_port, self.rule, self.logger, self.should_stop
            )
            executor.execute()

    def switch_to_rule_module(self) -> FramePort:
        """
        Switches the WebDriver to the rule modal frame to interact with rule elements.
        """
        self.logging("Switching to the Rule Modal...", "INFO")
        return self.browser_port.frame_locator('iframe[name="RadWindowAddEditRule"]')

    def set_rule_name(self, frame_port: FramePort, rule_name: str) -> None:
        """
        Sets the rule name in the rule creation form.
        """
        self.logging("Setting the Rule Name...", "INFO")

        frame_port.fill('[id*="overlayRuleProgressArea_tbRuleName"]', rule_name)

    def next_page(self, frame_port: FramePort) -> None:
        """
        Navigates to the next page in the rule creation form.
        """
        self.logging("Navigating to the Next Page...", "INFO")

        frame_port.click('[id*="overlayButtons_rbContinue_input"]')

    def is_tutorial_page_present(self, frame_port: FramePort) -> bool:
        """
        Checks if the tutorial page is present and can be skipped.

        Returns:
            bool: True if the tutorial page is present, False otherwise.
        """
        return frame_port.is_visible('[id*="overlayButtonsLeft_cbDontAskLead"]')

    def submit_rule(self, frame_port: FramePort) -> None:
        """
        Submits the rule form, handling duplicate rule alerts by renaming the rule and retrying.
        """

        self.logging(f"Submitting Rule - {self.rule_name }...", "INFO")

        def submit_rule_succeed():
            for _ in range(2):

                # Retry twice before giving up

                alert = self.browser_port.frame_click_and_accept_alert_if_appears(
                    frame_port,
                    '[id*="overlayButtons_rbSubmit_input"]',
                    "A Rule with this name already exists",
                    10000,
                )
                if alert:
                    self.rename_rule(frame_port)
                    self.logging(
                        f"Retrying Rule Submission for renamed rule - {self.rule_name }...",
                        "INFO",
                    )
                    continue

                else:
                    return True  # No alert found, submission is successful
            return False

        if not submit_rule_succeed():
            self.logging(
                f"Rule '{self.rule_name}' could not be submitted after multiple retries.",
                "ERROR",
            )
            raise DuplicateRuleNameException

        # self.browser_port.switch_to_main_frame()
        self.success_message()

    def rename_rule(self, frame_port: FramePort) -> None:
        """
        Renames the rule in case of a duplicate name error.
        """
        self.rule_rename_attempts += 1
        old_rule_name = self.rule.rule_name
        self.rule_name = f"{old_rule_name}-{self.rule_rename_attempts}"
        self.logging(
            f"Trying to rename rule: {old_rule_name} as {self.rule_name}",
            "WARN",
        )
        self.set_rule_name(frame_port, self.rule_name)

    def success_message(self) -> None:
        """
        Logs a success message after the rule has been successfully created.
        """
        success = self.browser_port.is_visible(
            "#ctl00_ActionBarContent_rbAction_Add", 10000
        )
        print(success, "*******************")
        if not success:
            raise RuntimeError("No Success Message")
        self.logging(f"Rule: {self.rule_name} has been created.", "INFO")

    def set_rule_category(self, frame_port: FramePort) -> None:
        """
        Sets the rule category in the rule creation form.
        """
        self.logging("Setting the rule category", "INFO")
        frame_port.click(
            '//*[contains(@id, "overlayContent_divAddEditAction")]/div[3]/a'
        )

        category_frame = self.browser_port.frame_locator(
            'iframe[name="RadWindowAddEditRuleSettings"]'
        )
        category_frame.click('[id*="ddRuleCategory_Arrow"]')
        category_frame.select_exact_item_from_list(
            '//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
            self.rule.rule_category,
        )
        self.logging("Switching the main frame", "INFO")

    def wait_for_dup_rule_alert(self, wait_time: int) -> bool:
        """
        Waits for a duplicate rule alert and handles it by accepting the alert.
        Returns:
            bool: True if the alert is found and accepted, False otherwise.
        """
        alert_present = self.browser_port.click_and_accept_alert_if_appears()
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

    def _build_stopped_result(self):
        return RuleExecutionResult(
            rule_guid=self.rule.guid,
            rule_name=self.rule.rule_name,
            success=False,
            status=RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
            message="Rule runner was stopped.",
        )
