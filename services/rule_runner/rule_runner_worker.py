from __future__ import annotations

from typing import TYPE_CHECKING, Deque

if TYPE_CHECKING:
    from ..rules.models import Rule
    from ..auth.auth_service import AuthService
    from ..auth.models.auth_result import AuthResult
    from ..intra.intra_provider_session import IntraProviderSession
    from services.logger.adapters import LogAdapter
from PySide6.QtCore import Signal, Slot, QObject
import threading
from collections import deque


from services.auth.enums import PROVIDERS

# from rulerunner.rule_worker import RuleWorker
from .executors import RuleExecutor
from .models import RuleRunnerConfig, RuleRunItem, RuleExecutionResult
from .enums import RULERUNSTATUS, RULEEXECSTATUS
from services.selenium import WebDriverManager
from services.selenium.adapters import SeleniumBrowserAdapter
from ..auth.enums import AUTHSTATUS


class RuleRunnerWorker(QObject):
    done = Signal()
    progress = Signal(int, int)

    def __init__(
        self,
        rules: list[Rule],
        config: RuleRunnerConfig,
        session: IntraProviderSession,
        auth_service: AuthService,
        logger: LogAdapter,
    ):
        super().__init__()
        self.rule_queue: Deque[RuleRunItem] = deque()
        self.config = config
        self.logger = logger

        self.session = session
        self.auth_service = auth_service

        for rule in rules:
            self.rule_queue.append(
                RuleRunItem(
                    rule_guid=rule.guid, rule=rule, status=RULERUNSTATUS.PENDING
                )
            )
        # TODO Remove Later: ONLY FOR TESTING
        # self.tenant = ""
        # self.username = ""
        # self.password = ""
        # self.url = ""
        # self.platform_version = "v10"

        self.driver = None
        self.driver_adapter = None
        self.current_executor: RuleExecutor | None = None
        self.errored_rules = []
        self.success_rules = []
        self.completed_count = 0
        self.total_count = len(self.rule_queue)
        self.shut_down = False

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def do_work(self):
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        try:
            self._init_driver()
            self.run_queue()

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
        self.driver_adapter = SeleniumBrowserAdapter(self.driver, self.logger)

    def _close_down_driver(self):
        """
        Closes and cleans up the Selenium WebDriver instance.
        """
        if self.driver_manager:
            self.driver = None
            self.driver_manager.close()
            self.driver_manager.deleteLater()

    def _rebuild_browser(self):
        self._close_down_driver()
        self._init_driver()

    def _authenticate(self) -> AuthResult:
        auth_attempts = 0
        max_attempts = 2
        while auth_attempts < max_attempts:
            self.logging(
                f"Attempting to authenticate: {auth_attempts} / {max_attempts-1}"
            )
            result = self.auth_service.ensure_auth(
                PROVIDERS.INTRA, self.creds, self.driver_adapter
            )

            if result.success:
                self.logging("Received Successful Authentication.")
                return result
            self.logging("Received Failure Authentication.", "WARN")
            if result.status == AUTHSTATUS.BROWSER_ERROR:
                self._rebuild_browser()
            auth_attempts += 1
        self.logging(
            "Attempted to log in 2 times. Login Failed due to an error.", "ERROR"
        )
        return result

    def run_queue(self):
        auth_result = self._authenticate()
        if not auth_result.success:
            self.shut_down = True
            self._drain_remaining_rules(RULERUNSTATUS.FAILED, "Failed to Authenticate")

        while self.rule_queue and not self.shut_down:
            self.progress.emit(self.completed_count, self.total_count)
            try:
                item = self.rule_queue.popleft()
                item.status = RULERUNSTATUS.RUNNING
                self.current_executor = RuleExecutor(
                    self.url, self.driver_adapter, item.rule, self.logger
                )
                result = self.current_executor.execute()
                self._handle_result(item, result)

            except Exception as e:
                print(e)
                self.logging(
                    f"Failure trying to process next rule: {e}",
                    "ERROR",
                )
        self.progress.emit(self.completed_count, self.total_count)
        self.create_rule_summary()
        self.close()

    def _handle_result(self, item: RuleRunItem, result: RuleExecutionResult):
        self.logging(f"Recieved result for {result.rule_name}")
        if result.success:
            self.logging(f"{result.rule_name} - succeeded.")
            item.status = RULERUNSTATUS.SUCCESS
            item.rule.rule_name = result.rule_name
            self.success_rules.append(item)
            self.completed_count += 1
        else:
            self.logging(f"{result.rule_name} - failed.")
            if item.retry_count < 2:
                item.retry_count += 1
                if result.status in (RULEEXECSTATUS.NAME_EXISTS_ERROR):
                    item.status = RULERUNSTATUS.FAILED
                    self.errored_rules.append(item)
                    self.completed_count += 1
                    self.logging(f"{result.rule_name} - not retrying running rule.")
                elif result.status in (
                    RULEEXECSTATUS.BROWSER_ERROR,
                    RULEEXECSTATUS.UNKNOWN_ERROR,
                ):
                    self.logging(f"{result.rule_name} - retrying running rule.")
                    item.status = RULERUNSTATUS.RETRYING
                    self.rule_queue.appendleft(item)
                    self._rebuild_browser()
                    auth_result = self._authenticate()
                    if not auth_result.success:
                        self.shut_down = True
                        self._drain_remaining_rules(
                            RULERUNSTATUS.FAILED, "Authentication failed during retry"
                        )
            else:
                self.logging(f"{result.rule_name} - not retrying running rule.")
                item.status = RULERUNSTATUS.FAILED
                self.errored_rules.append(item)
                self.completed_count += 1

    def create_rule_summary(self) -> None:
        """
        Creates a summary of successfully executed and errored rules.
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

    def _drain_remaining_rules(self, status: RULERUNSTATUS, reason: str):
        while self.rule_queue:
            item = self.rule_queue.popleft()
            item.status = status
            self.errored_rules.append(item)

        self.logging(f"Removing remaining rules from queue: {reason}", "WARN")

    @Slot()
    def stop(self) -> None:
        """
        Stops the thread execution.
        """
        self.logging("Stop Button Pressed", "INFO")
        self.logging("Shutting down", "INFO")
        self.shut_down = True
        if self.current_executor:
            self.current_executor.stop_requested = True
        self._drain_remaining_rules(
            RULERUNSTATUS.STOPPED, "Rule runner manually stopped."
        )
        self.close()

    def close(self) -> None:
        """
        Closes the thread and ensures proper shutdown of all resources.
        """
        self._close_down_driver()
        self.done.emit()
