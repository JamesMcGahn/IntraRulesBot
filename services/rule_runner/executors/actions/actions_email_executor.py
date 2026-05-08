from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...interfaces import BrowserPort
    from ....rules.models import Rule
    from ....rules.models.actions import ActionsEmailDetails
    from ....logger.adapters import LogAdapter
from time import sleep
import threading

from selenium.webdriver.common.by import By

from ..wrappers import ExecutorWrappers


class ActionsEmailExecutor:
    """
    Worker class responsible for handling email-related actions within rules.
    This worker interacts with the UI to set up and send emails based on rule
    configurations using Selenium WebDriver.
    """

    def __init__(
        self,
        browser_port: BrowserPort,
        rule: Rule,
        index: int,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        super().__init__()
        self.browser_port = browser_port
        self.rule = rule
        self.index = index
        self.action = None
        self.logger = logger
        self.should_stop = should_stop

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    @ExecutorWrappers.child_raise_error
    def execute(self) -> None:
        """
        Executes the steps required to perform the email action, including navigating
        to the email settings page, setting the email subject, message, and address,
        and completing the email setup. Emits the finished signal when complete.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )

        try:
            self.action = self.rule.actions[self.index]
        except IndexError as _:
            self.logging(
                f"Condition index {self.index} is out of range for {self.rule.rule_name}",
                "ERROR",
            )
            raise IndexError from IndexError

        action_details: ActionsEmailDetails = self.action.details

        self.click_email_settings_page()
        self.set_email_subject(self.rule.rule_name)
        self.set_email_message(action_details)
        self.click_next_page()
        self.set_email_address(action_details)

    def click_email_settings_page(self) -> None:
        """
        Clicks on the email settings button to open the email configuration page.
        """
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_lblSettings")]',
        )

    def set_email_subject(self, rule_name: str) -> None:
        """
        Sets the subject of the email based on the rule name.
        """
        self.logging(f"Setting email subject for Action {self.index+1}...", "INFO")
        self.browser_port.wait_and_type(
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_ctl05")]',
            rule_name,
        )

    def set_email_message(self, action_details: ActionsEmailDetails) -> None:
        """
        Sets the email message body based on the provided action details.
        """
        self.logging(f"Setting email message for Action {self.index+1}...", "INFO")
        sleep(1)
        email_message_one = self.browser_port.wait_for_element(
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_ctl12")]',
            retries=1,
        )
        if email_message_one:
            self.browser_port.wait_and_type(
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl12")]',
                action_details.email_body,
            )
        else:
            self.browser_port.wait_and_type(
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl13")]',
                action_details.email_body,
            )

        sleep(1)

    def click_next_page(self) -> None:
        """
        Clicks the next button to proceed to the next step in the email configuration.
        """
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
        )

    def set_email_address(self, action_details: ActionsEmailDetails) -> None:
        """
        Sets the recipient email address based on the rule condition source
        and the provided action details.
        """
        self.logging(
            f"Setting receiver email address for Action {self.index+1}...", "INFO"
        )
        self.browser_port.wait_and_click(
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_rblIntradiemUsersIndividual_Users_1")]',
        )
        self.logging("Trying to find which email body rule uses...")
        email_body_one = self.browser_port.wait_for_element(
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
            retries=1,
        )
        if email_body_one:
            self.browser_port.wait_and_type(
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
                action_details.email_address,
            )
        else:
            self.browser_port.wait_and_type(
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl61")]',
                action_details.email_address,
            )
