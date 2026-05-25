from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService
    from ..browser import BrowserSessionFactory
    from .intra_provider_session import IntraProviderSession
    from services.logger.adapters import LogAdapter
    from services.browser.models import PlaywrightSession

from threading import Event, get_ident

from PySide6.QtCore import QObject, Signal

from services.auth.enums import PROVIDERS
from services.browser.models import PlaywrightConfig

from ..auth.enums import AUTHSTATUS
from ..auth.models.auth_result import AuthResult
from ..rule_runner.models import RuleRunnerConfig


class IntraLoginWorker(QObject):
    done = Signal()
    is_valid = Signal(str, bool)

    def __init__(
        self,
        job_id,
        batch,
        browser_session_factory: BrowserSessionFactory,
        session: IntraProviderSession,
        auth_service: AuthService,
        logger: LogAdapter,
    ):
        super().__init__()
        self.logger = logger
        self.session = session
        self.auth_service = auth_service
        self.browser_session_factory = browser_session_factory
        self.job_id = job_id
        self.tenant = batch.get("tenant")
        self.username = batch.get("user_name")
        self.password = batch.get("password")
        self.url = f"https://{self.tenant}.intradiem.com/"
        self.platform_version = batch.get("platform_version")

        self.creds = RuleRunnerConfig(
            self.username,
            self.password,
            self.tenant,
            self.platform_version,
            login_valid=False,
        )

        self.playwright_session_manager = None
        self.playwright_session: PlaywrightSession | None = None
        self._shut_down = Event()

    def should_stop(self) -> bool:
        return self._shut_down.is_set()

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def do_work(self):
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {get_ident()}",
            "INFO",
        )
        try:
            self._init_browser(False)
            self._authenticate()

        except Exception as e:
            if not self.should_stop():
                self.logging(f"{e}", "DEBUG")
                self.logging("Fatal Error", "ERROR")
            self.is_valid.emit(self.job_id, False)

        finally:
            self.close()

    def _init_browser(self, load_session_cookies=False) -> None:
        """
        Initializes the Selenium WebDriver through the WebDriverManager.
        """
        self.playwright_session_manager = self.browser_session_factory.create_session(
            PROVIDERS.INTRA, PlaywrightConfig()
        )
        self.playwright_session = self.playwright_session_manager.start()

    def _close_down_browser(self):
        if not self.playwright_session_manager:
            return
        self.playwright_session_manager.close()
        self.playwright_session_manager = None
        self.playwright_session = None

    def _authenticate(self) -> AuthResult:
        auth_attempts = 0
        max_attempts = 2

        while auth_attempts < max_attempts:
            if self.should_stop():
                return AuthResult(success=False, status=AUTHSTATUS.STOPPED_REQUESTED)
            self.logging(
                f"Attempting to authenticate: {auth_attempts} / {max_attempts-1}"
            )
            result = self.auth_service.ensure_auth(
                PROVIDERS.INTRA,
                self.creds,
                self.playwright_session.browser_adapter,
                should_stop_cb=self.should_stop,
            )

            if result.success:
                self.logging("Received Successful Authentication.")
                return self.is_valid.emit(self.job_id, result.success)
            self.logging("Received Failure Authentication.", "WARN")
            if result.status == AUTHSTATUS.BROWSER_ERROR:
                self._init_browser()
            auth_attempts += 1
        self.logging(
            "Attempted to log in 2 times. Login Failed due to an error.", "ERROR"
        )
        return self.is_valid.emit(self.job_id, result.success)

    def close(self) -> None:
        """
        Closes the thread and ensures proper shutdown of all resources.
        """
        self._close_down_browser()
        self.done.emit()

    def request_shut_down(self) -> None:
        self.logging("Requested Shut Down.", "INFO")
        self._shut_down.set()
