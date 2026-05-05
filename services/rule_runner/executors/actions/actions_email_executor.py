from time import sleep
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By

from base import ErrorWrappers

from rulerunner.utils import WaitConditions, WebElementInteractions


class ActionsEmailExecutor:
    """
    Worker class responsible for handling email-related actions within rules.
    This worker interacts with the UI to set up and send emails based on rule
    configurations using Selenium WebDriver.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.
        action (dict): The email action data that contains the details such as email body and address.
        rule (dict): The rule data
        index (int): The index of the current action in the list of actions.
        wELI (WebElementInteractions): Instance for interacting with web elements in the browser.
        _rule_condition_queues_source (str): The source of the rule condition, either "users" or "queues".

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        actions_worker (ActionsWorker): The actions worker that provides shared resources for handling actions.
        action (dict): The specific action data related to sending the email.
        rule (dict): The rule data
        index (int): The index of the action within the current rule's list of actions.
    """

    def __init__(
        self,
        driver: webdriver.Chrome,
        actions_worker,
        action: dict,
        rule: dict,
        index: int,
        logger,
    ):
        """
        Initializes the ActionsEmailWorker with the provided driver, action, rule, and index.
        Connects logging to web element interactions and sets up internal references for rule processing.
        """
        super().__init__()
        self.driver = driver
        self.action = action
        self.rule = rule
        self.index = index
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = actions_worker.rule_condition_queues_source
        self.wELI.send_msg.connect(self.logging)
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
        Executes the steps required to perform the email action, including navigating
        to the email settings page, setting the email subject, message, and address,
        and completing the email setup. Emits the finished signal when complete.

        Returns:
            None: This function does not return a value.
        """
        self.log_thread()
        self.click_email_settings_page()
        self.set_email_subject(self.rule["rule_name"])
        self.set_email_message(self.action)
        self.click_next_page()
        self.set_email_address(self.action)

    def click_email_settings_page(self) -> None:
        """
        Clicks on the email settings button to open the email configuration page.

        Returns:
            None: This function does not return a value.
        """

        email_page_settings_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_lblSettings")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        email_page_settings_btn.click()

    def set_email_subject(self, rule_name: str) -> None:
        """
        Sets the subject of the email based on the rule name.

        Args:
            rule_name (str): The name of the rule used as the email subject.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Setting email subject for Action {self.index+1}...", "INFO")
        email_subject = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_ctl05")]',
            WaitConditions.VISIBILITY,
            raise_exception=True,
        )
        email_subject.send_keys(rule_name)

    def set_email_message(self, action: dict) -> None:
        """
        Sets the email message body based on the provided action details.

        Args:
            action (dict): The action data containing the email body text.

        Returns:
            None: This function does not return a value.
        """
        self.logging(f"Setting email message for Action {self.index+1}...", "INFO")
        sleep(1)
        if "frequency_based" in self.rule:
            email_message = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl12")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )
        else:
            email_message = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl13")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )

        email_message.send_keys(action["details"]["email_body"])
        sleep(1)

    def click_next_page(self) -> None:
        """
        Clicks the next button to proceed to the next step in the email configuration.

        Returns:
            None: This function does not return a value.
        """
        continue_btn = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayButtons_rbContinue_input")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        continue_btn.click()

    def set_email_address(self, action) -> None:
        """
        Sets the recipient email address based on the rule condition source
        and the provided action details.

        Args:
            action (dict): The action data containing the email recipient address.

        Returns:
            None: This function does not return a value.
        """
        self.logging(
            f"Setting receiver email address for Action {self.index+1}...", "INFO"
        )
        select_email_individual = self.wELI.wait_for_element(
            20,
            By.XPATH,
            '//*[contains(@id, "overlayContent_actionParameters_rblIntradiemUsersIndividual_Users_1")]',
            WaitConditions.CLICKABLE,
            raise_exception=True,
        )
        select_email_individual.click()

        if self._rule_condition_queues_source == "users":
            input_email_address = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )

        elif self._rule_condition_queues_source == "queues":
            input_email_address = self.wELI.wait_for_element(
                20,
                By.XPATH,
                '//*[contains(@id, "overlayContent_actionParameters_ctl61")]',
                WaitConditions.VISIBILITY,
                raise_exception=True,
            )

        input_email_address.send_keys(action["details"]["email_address"])
