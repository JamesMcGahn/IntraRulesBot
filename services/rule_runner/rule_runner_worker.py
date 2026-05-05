from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..rules.models import Rule

from PySide6.QtCore import Signal, Slot, QObject
import threading
from collections import deque

from selenium.common.exceptions import NoSuchWindowException, WebDriverException


from rulerunner.login import LoginManagerWorker
from services.logger import Logger
from services.logger.adapters import LogAdapter

# from rulerunner.rule_worker import RuleWorker
from .executors import RuleExecutor
from .models import RuleRunnerConfig
from services.selenium import SeleniumBrowserAdapter, WebDriverManager


class RuleRunnerWorker(QObject):
    done = Signal()
    progress = Signal(int, int)

    def __init__(self, rules: list[Rule], config: RuleRunnerConfig):
        super().__init__()
        self.rules = deque(rules)
        self.config = config
        self.logger = Logger()
        self.logging = LogAdapter(self.logger)
        self.rules_total_count = len(rules)

        # TODO Remove Later: ONLY FOR TESTING

        self.username = ""
        self.password = ""
        self.url = ""

        self.driver = None
        self.driver_adapter = None

        self._rule_finished = False
        self.current_rule = None
        self.errors_in_a_row = 0
        self.errored_rules = []
        self.success_rules = []
        self.login_attempt = False
        self.shut_down = False

    def do_work(self):
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        print("here")
        try:
            self._init_driver()
            self.get_login_url()
            self.start_login()

        except Exception as e:
            print(e)
            self.logging("Fatal Error", "ERROR")

    def _init_driver(self) -> None:
        """
        Initializes the Selenium WebDriver through the WebDriverManager.
        """
        self.driver_manager = WebDriverManager()
        self.driver_manager.init_driver()
        self.driver = self.driver_manager.get_driver()
        self.driver_adapter = SeleniumBrowserAdapter(self.driver, self.logging)

    def close_down_driver(self):
        """
        Closes and cleans up the Selenium WebDriver instance.
        """
        self.driver_manager.close()
        self.driver_manager.deleteLater()

    def start_login(self):
        self.login_worker = LoginManagerWorker(
            self.driver,
            self.username,
            self.password,
            self.url,
        )

        # self.login_worker.send_logs.connect(self.logging)
        self.login_worker.error.connect(self.login_error)
        self.login_worker.success.connect(self.login_success)

        self.login_worker.do_work()

    def get_login_url(self) -> None:
        """
        Loads the login URL in the browser. Handles exceptions such as browser closure
        and retries if necessary.
        """
        if self.shut_down:
            return
        try:
            self.driver.get(self.url)
            self.logging(f"Loaded in the browser: {self.url} ", "INFO")
        except NoSuchWindowException:
            self.logging("Error loading URL. Browser closed.", "ERROR")
            self.logging("Restarting WebDriver.....", "INFO")
            if not self.shut_down:
                self._init_driver()
                self.driver.get(self.url)
        except WebDriverException as e:
            if not self.shut_down:
                self.logging(
                    f"Error loading URL. Browser likely closed: {str(e)}", "ERROR"
                )
                self.logging("Restarting WebDriver.....", "INFO")
                self._init_driver()
                self.driver.get(self.url)
        except Exception as e:
            self.logging(f"Error loading URL.: {str(e)}", "ERROR")
            if not self.shut_down:
                self.close()

    # TODO
    @Slot()
    def login_error(self) -> None:
        """
        Handles login errors. Retries login if it hasn't been attempted, otherwise shuts down the thread.

        Returns:
            None: This function does not return a value.
        """

        if not self.login_attempt and not self.shut_down:
            self.login_attempt = True
            self.logging("Login Failed due to an error. Retrying again.", "INFO")
            self.get_login_url()
            self.start_login()
        else:
            if not self.shut_down:
                self.logging(
                    "Login Failed due to an error. Shutting down thread", "ERROR"
                )
                self.close()

    @Slot()
    def login_success(self) -> None:
        """
        Processes the next rule after a successful login.

        Returns:
            None: This function does not return a value.
        """
        self.process_next_rule()

    # TODO : Re design rule flow
    def process_next_rule(self) -> None:
        """
        Processes the next rule in the queue by initializing and running the RuleWorker.

        Returns:
            None: This function does not return a value.
        """
        if self.shut_down:
            return
        rules_length = len(self.rules)
        self.progress.emit(
            self.rules_total_count - rules_length, self.rules_total_count
        )
        if rules_length > 0:
            try:
                self.current_rule = self.rules.popleft()
                self.executor = RuleExecutor(
                    self.driver_adapter, self.current_rule, self.logging
                )

                # self.rule_worker.error.connect(self.on_rule_error)
                self.executor.execute()
                # self.on_rule_finished(self.current_rule.get("rule_name"))
            except Exception as e:
                print(e)
                self.logging(
                    f"Failure trying to process next rule: {e}",
                    "ERROR",
                )

        else:
            self.create_rule_summary()
            self.close()

    def create_rule_summary(self) -> None:
        """
        Creates a summary of successfully executed and errored rules.

        Returns:
            None: This function does not return a value.
        """
        errored_rules_msg = f"ERRORED RULES TOTAL: {len(self.errored_rules)} \n"
        succeeded_rules_msg = f"SUCCEEDED RULES TOTAL: {len(self.success_rules)} \n"
        tabs = "\t" * 4
        for e_rule_name in self.errored_rules:
            errored_rules_msg += f"{tabs}- {e_rule_name} \n"
        for s_rule_rume in self.success_rules:
            succeeded_rules_msg += f"{tabs}- {s_rule_rume} \n"
        self.logging(succeeded_rules_msg, "INFO")
        self.logging(errored_rules_msg, "ERROR")

    @Slot(str)
    def on_rule_finished(self, rule_name: str) -> None:
        """
        Handles the completion of a rule and proceeds to process the next one.

        Args:
            rule_name (str): The name of the rule that was successfully created.

        Returns:
            None: This function does not return a value.
        """
        self.logging("RuleWorker finished.", "INFO")
        self.success_rules.append(rule_name)
        # self.rule_created.emit(rule_name)
        self.errors_in_a_row = 0
        self.process_next_rule()

    @Slot(bool)
    def on_rule_error(self, shouldRetry: bool) -> None:
        """
        Handles rule processing errors and decides whether to retry or skip the rule.

        Args:
            shouldRetry (bool): Indicates whether to retry the rule.

        Returns:
            None: This function does not return a value.
        """
        self.errors_in_a_row += 1
        self.logging("RuleRunnerThread received error from Rule Worker.", "WARN")
        self.logging(
            f"Rule: {self.current_rule["rule_name"]} has errored out {self.errors_in_a_row} times.",
            "WARN",
        )
        if self.errors_in_a_row < 2 and shouldRetry and not self.shut_down:
            self.logging(
                f"Trying Again to create Rule for {self.current_rule["rule_name"]}",
                "INFO",
            )
            self.rules.appendleft(self.current_rule)
            self.get_login_url()
            self.start_login()
        else:
            if self.shut_down:
                return
            msg = (
                f"Skipping Rule due to {self.errors_in_a_row} errors in a row"
                if shouldRetry
                else "Skipping Rule - "
            )
            if not self.shut_down:

                self.logging(msg, "INFO")
            self.errored_rules.append(self.current_rule["rule_name"])
            if len(self.rules) > 0:
                self.get_login_url()
                self.start_login()
                self.errors_in_a_row = 0
            else:
                self.create_rule_summary()
                self.close()

    @Slot()
    def stop(self) -> None:
        """
        Stops the thread execution.

        Returns:
            None: This function does not return a value.
        """

        self.logging("Stop Button Pressed", "INFO")
        self.logging(
            f"Shutting down RuleRunnerThread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )
        self.shut_down = True
        self.close()

    @Slot(bool)
    def close(self) -> None:
        """
        Closes the thread and ensures proper shutdown of all resources.

        Returns:
            None: This function does not return a value.
        """
        self.close_down_driver()
        self.done.emit()
