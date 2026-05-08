from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService

    from .intra_provider_session import IntraProviderSession
    from services.logger.adapters import LogAdapter
from PySide6.QtCore import Signal, QObject
import threading


from services.auth.enums import PROVIDERS

from ..rule_runner.models import RuleRunnerConfig
from services.selenium import WebDriverManager
from services.selenium.adapters import SeleniumBrowserAdapter
from ..auth.enums import AUTHSTATUS
from ..auth.models.auth_result import AuthResult


class IntraLoginWorker(QObject):
    done = Signal()
    is_valid = Signal(str, bool)

    def __init__(
        self,
        job_id,
        batch,
        session: IntraProviderSession,
        auth_service: AuthService,
        logger: LogAdapter,
    ):
        super().__init__()
        print(batch)
        self.logger = logger
        self.session = session
        self.auth_service = auth_service
        self.job_id = job_id
        self.tenant = batch.get("tenant")
        self.username = batch.get("user_name")
        self.password = batch.get("password")
        self.url = f"https://{self.tenant}.intradiem.com/"
        self.platform_version = "v10"

        self.creds = RuleRunnerConfig(
            self.username, self.password, self.tenant, self.platform_version
        )

        self.driver = None
        self.driver_adapter = None
        self.shut_down = False

    def should_stop(self) -> bool:
        return self.shut_down

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def do_work(self):
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
            "INFO",
        )
        try:
            self._init_driver(False)
            self._authenticate()
            self.close()

        except Exception as e:
            print(e)
            self.logging("Fatal Error", "ERROR")
            self.is_valid.emit(self.job_id, False)
            self.close()

    def _init_driver(self, load_session_cookies=False) -> None:
        """
        Initializes the Selenium WebDriver through the WebDriverManager.
        """
        self.driver_manager = WebDriverManager()
        self.driver_manager.init_driver()
        self.driver = self.driver_manager.get_driver()
        self.driver_adapter = SeleniumBrowserAdapter(self.driver, self.logger)
        self.driver.get(self.url)
        if load_session_cookies:
            self.load_cookies()

    def load_cookies(self) -> None:
        cookies = self.session.convert_jar_to_cookie_list()
        self.driver_manager.load_cookies(cookies)

    def save_cookies(self) -> None:
        cookies = self.driver_manager.get_cookies()
        self.session.update_cookies_from_list(cookies)
        self.session.save_session()

    def _close_down_driver(self):
        if not self.driver_manager:
            return

        try:
            self.save_cookies()
        except Exception as e:
            if self.shut_down:
                return
            self.logging(f"Skipping cookie save during driver shutdown: {e}", "WARN")

        try:
            self.driver_manager.close()
        except Exception as e:
            if self.shut_down:
                return
            self.logging(f"Error closing driver: {e}", "WARN")

        self.driver = None
        self.driver_adapter = None
        self.driver_manager = None

    def _authenticate(self) -> AuthResult:
        auth_attempts = 0
        max_attempts = 2

        while auth_attempts < max_attempts:
            if self.shut_down:
                return AuthResult(success=False, status=AUTHSTATUS.STOPPED_REQUESTED)
            self.logging(
                f"Attempting to authenticate: {auth_attempts} / {max_attempts-1}"
            )
            result = self.auth_service.ensure_auth(
                PROVIDERS.INTRA,
                self.creds,
                self.driver_adapter,
                should_stop_cb=self.should_stop,
            )

            if result.success:
                self.logging("Received Successful Authentication.")
                return self.is_valid.emit(self.job_id, result.success)
            self.logging("Received Failure Authentication.", "WARN")
            if result.status == AUTHSTATUS.BROWSER_ERROR:
                self._rebuild_browser()
            auth_attempts += 1
        self.logging(
            "Attempted to log in 2 times. Login Failed due to an error.", "ERROR"
        )
        return self.is_valid.emit(self.job_id, result.success)

    def close(self) -> None:
        """
        Closes the thread and ensures proper shutdown of all resources.
        """
        self._close_down_driver()
        self.done.emit()
