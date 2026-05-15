from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ....browser.ports import FramePort
    from ....rules.models import Rule
    from ....rules.models.actions import ActionsEmailDetails
    from ....logger.adapters import LogAdapter
import threading


from ..wrappers import ExecutorWrappers


class ActionsEmailExecutor:
    """
    Worker class responsible for handling email-related actions within rules.
    This worker interacts with the UI to set up and send emails based on rule
    configurations using Selenium WebDriver.
    """

    def __init__(
        self,
        frame_port: FramePort,
        rule: Rule,
        index: int,
        logger: LogAdapter,
        should_stop: Callable,
    ):
        super().__init__()
        self.frame_port = frame_port
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
        self.frame_port.click('[id*="overlayContent_actionParameters_lblSettings"]')

    def set_email_subject(self, rule_name: str) -> None:
        """
        Sets the subject of the email based on the rule name.
        """
        self.logging(f"Setting email subject for Action {self.index+1}...", "INFO")
        self.frame_port.fill('[id*="overlayContent_actionParameters_ctl05"]', rule_name)

    def set_email_message(self, action_details: ActionsEmailDetails) -> None:
        """
        Sets the email message body based on the provided action details.
        """
        self.logging(f"Setting email message for Action {self.index+1}...", "INFO")

        email_message_one = self.frame_port.is_visible(
            '[id*="overlayContent_actionParameters_ctl12"]', 3000
        )

        if email_message_one:
            self.frame_port.fill(
                '[id*="overlayContent_actionParameters_ctl12"]',
                action_details.email_body,
            )
        else:
            self.frame_port.fill(
                '[id*="overlayContent_actionParameters_ctl13"]',
                action_details.email_body,
            )

    def click_next_page(self) -> None:
        """
        Clicks the next button to proceed to the next step in the email configuration.
        """
        self.frame_port.click('[id*="overlayButtons_rbContinue_input"]')

    def set_email_address(self, action_details: ActionsEmailDetails) -> None:
        """
        Sets the recipient email address based on the rule condition source
        and the provided action details.
        """
        self.logging(
            f"Setting receiver email address for Action {self.index+1}...", "INFO"
        )
        self.frame_port.click(
            '[id*="overlayContent_actionParameters_rblIntradiemUsersIndividual_Users_1"]'
        )

        self.logging("Trying to find which email body rule uses...")
        email_body_one = self.frame_port.is_visible(
            '[id*="overlayContent_actionParameters_ctl65"]'
        )
        if email_body_one:
            self.frame_port.fill(
                '[id*="overlayContent_actionParameters_ctl65"]',
                action_details.email_address,
            )
        else:
            self.frame_port.fill(
                '[id*="overlayContent_actionParameters_ctl61"]',
                action_details.email_address,
            )
