from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..auth.session.session_registry import SessionRegistry
    from ..auth.enums import PROVIDERS

    from services.logger.adapters import LogAdapter
    from services.browser.ports import BrowserPort
    from .models.intra_login import IntraLogin

import time

from ..auth.models.auth_validation_response import AuthValidationResponse
from ..auth.base_auth_service import BaseAuthService
from ..auth.enums.auth_status import AUTHSTATUS
from ..auth.models.auth_result import AuthResult
from playwright.sync_api import Error as PlaywrightError


class IntraAuthService(BaseAuthService):

    def __init__(
        self, session_registry: SessionRegistry, provider: PROVIDERS, logger: LogAdapter
    ):
        super().__init__(session_registry, provider, logger)

        self.last_login_attempt = None
        self.login_cooldown_seconds = self.session.login_cool_down

    def validate(self) -> AuthValidationResponse:
        self.logging("Validating auth session credentials...")
        has_valid_cookies = self.session.has_valid_auth_cookies()

        return AuthValidationResponse(
            provider=self.provider_name,
            cookies_valid=has_valid_cookies,
            token_valid=False,
        )

    def ensure_auth(
        self,
        creds: IntraLogin,
        browser_port: BrowserPort,
        force_login=True,
        should_stop_cb: Callable[[], bool] | None = None,
    ) -> AuthResult:

        result = self.validate()
        if not force_login and result.cookies_valid:
            return AuthResult(
                success=True,
                status=AUTHSTATUS.ALREADY_AUTHENTICATED,
                message=f"{self.provider_name} is authenticated.",
            )

        if not force_login and not self.can_attempt_login():
            self.logging("Login cooldown active", "WARN")
            return AuthResult(
                success=False,
                status=AUTHSTATUS.COOLDOWN,
                message="Login cooldown active",
            )

        return self.login(creds, browser_port, should_stop_cb)

    def login(
        self, creds: IntraLogin, browser_port: BrowserPort, should_stop_cb
    ) -> AuthResult:
        result = self._perform_login(creds, browser_port, should_stop_cb)
        self.last_login_attempt = time.time()

        return result

    def _perform_login(
        self, creds: IntraLogin, browser_port: BrowserPort, should_stop_cb
    ):
        try:
            browser_port.goto(
                f"https://{creds.tenant}.intradiem.com/?loginoverride=manual"
            )
            browser_port.wait_for_page_ready()

            self._enter_login_info(creds, browser_port)
            self._wait_for_session_alert(browser_port)
            browser_port.wait_for_page_ready()
            return self._wait_for_success(browser_port)
        except PlaywrightError as e:
            if should_stop_cb is not None and should_stop_cb():
                self.logging("Stop Requested. Stopping Auth.")
                return AuthResult(
                    success=False,
                    status=AUTHSTATUS.STOPPED_REQUESTED,
                    message="Stop Requested",
                )
            msg = "Error Occurred while logging in. The browser was closed"
            self.logging(msg, "ERROR")
            self.logging(str(e), "DEBUG")
            return AuthResult(
                success=False, status=AUTHSTATUS.BROWSER_ERROR, message=msg
            )

        except Exception as e:
            if should_stop_cb is not None and should_stop_cb():
                self.logging("Stop Requested. Stopping Auth.")
                return AuthResult(
                    success=False,
                    status=AUTHSTATUS.STOPPED_REQUESTED,
                    message="Stop Requested",
                )
            self.logging(f"Error: {str(e)}", "ERROR")
            return AuthResult(
                success=False,
                status=AUTHSTATUS.UNKNOWN_ERROR,
                message="Error Occurred while logging in.",
            )

    def _enter_login_info(self, creds: IntraLogin, browser_port: BrowserPort) -> None:
        """
        Enters the username and password into the login fields and clicks the login button.
        """
        browser_port.fill("#inputUserName", creds.user_name)
        browser_port.fill("#inputPassword", creds.password)
        # browser_port.click("#btnLogin")
        alert = browser_port.click_and_accept_alert_if_appears("#btnLogin")
        if alert:
            self.logging(
                "Session open elsewhere alert was present. Accepted alert to proceed with this session.",
                "INFO",
            )
        else:
            self.logging("No session alert was present.", "INFO")

    def _wait_for_session_alert(self, browser_port: BrowserPort) -> None:
        """
        Waits for a session alert indicating that a session is open elsewhere, and accepts the alert if present.
        """
        pass
        # alert = browser_port.accept_alert_if_appears(None, 5000)

    def _wait_for_success(self, browser_port: BrowserPort) -> AuthResult:
        """
        Waits for the login success by checking for any error messages.
        """

        error_toast = browser_port.is_visible("#loginErrorContainer span", 5000)
        if error_toast:
            msg = f"Error during login: {error_toast.text}"
            self.logging(msg, "ERROR")
            return AuthResult(
                success=False, status=AUTHSTATUS.INVALID_CREDENTIALS, message=msg
            )
        self.logging("Login error toast not found. Verifying page loaded.", "INFO")
        main_page_content = browser_port.is_visible("#ctl00_contentWrapper", 5000)
        if main_page_content:
            msg = "Found main content on page. Login Successful."
            self.logging(msg)
            return AuthResult(success=True, status=AUTHSTATUS.SUCCESS, message=msg)
        else:
            msg = "Failure to find main content on page. Login Error."
            self.logging(msg)
            return AuthResult(
                success=False, status=AUTHSTATUS.BROWSER_ERROR, message=msg
            )
