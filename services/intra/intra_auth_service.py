from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..auth.session.session_registry import SessionRegistry
    from ..auth.enums import PROVIDERS

    from services.logger.adapters import LogAdapter
    from services.browser.ports import BrowserPort
    from .models.intra_login import IntraLogin
    from services.profiles import ProfileRegistry
    from services.profiles.models import LoginSelectors

import time

from playwright.sync_api import Error as PlaywrightError

from ..auth.base_auth_service import BaseAuthService
from ..auth.enums.auth_status import AUTHSTATUS
from ..auth.models.auth_result import AuthResult
from ..auth.models.auth_validation_response import AuthValidationResponse


class IntraAuthService(BaseAuthService):

    def __init__(
        self,
        session_registry: SessionRegistry,
        profile_registry: ProfileRegistry,
        provider: PROVIDERS,
        logger: LogAdapter,
    ):
        super().__init__(session_registry, profile_registry, provider, logger)

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
        profile = self.profile_registry.get_profile(creds.platform_version)
        log_selectors = profile.selectors.login
        return self.login(creds, browser_port, log_selectors, should_stop_cb)

    def login(
        self,
        creds: IntraLogin,
        browser_port: BrowserPort,
        selectors: LoginSelectors,
        should_stop_cb,
    ) -> AuthResult:
        result = self._perform_login(creds, browser_port, selectors, should_stop_cb)
        self.last_login_attempt = time.time()

        return result

    def _perform_login(
        self,
        creds: IntraLogin,
        browser_port: BrowserPort,
        selectors: LoginSelectors,
        should_stop_cb,
    ):
        try:
            self.check_shutdown(should_stop_cb)
            browser_port.goto(
                f"https://{creds.tenant}.intradiem.com/?loginoverride=manual"
            )
            self.check_shutdown(should_stop_cb)
            browser_port.wait_for_page_ready()
            self.check_shutdown(should_stop_cb)
            self._enter_login_info(creds, browser_port, selectors)
            self.check_shutdown(should_stop_cb)
            browser_port.wait_for_page_ready()
            self.check_shutdown(should_stop_cb)
            return self._wait_for_success(browser_port, selectors)
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

    def _enter_login_info(
        self, creds: IntraLogin, browser_port: BrowserPort, selectors: LoginSelectors
    ) -> None:
        """
        Enters the username and password into the login fields and clicks the login button.
        """

        browser_port.fill(selectors.user_name_input, creds.user_name)
        browser_port.fill(selectors.password_input, creds.password)

        alert = browser_port.click_and_accept_alert_if_appears(selectors.submit_button)
        if alert:
            self.logging(
                "Session open elsewhere alert was present. Accepted alert to proceed with this session.",
                "INFO",
            )
        else:
            self.logging("No session alert was present.", "INFO")

    def _wait_for_success(
        self, browser_port: BrowserPort, selectors: LoginSelectors
    ) -> AuthResult:
        """
        Waits for the login success by checking for any error messages.
        """

        error_toast = browser_port.is_visible(selectors.error_container, 3000)
        duplicate_session = browser_port.is_visible(selectors.logged_out_session, 3000)
        if error_toast:
            msg = "Error during login. Couldnt log in."
            self.logging(msg, "ERROR")
            return AuthResult(
                success=False, status=AUTHSTATUS.INVALID_CREDENTIALS, message=msg
            )
        if duplicate_session:
            msg = "You have logged out or have been logged out due to logging in from another session."
            self.logging(msg, "ERROR")
            return AuthResult(
                success=False, status=AUTHSTATUS.DUPLICATE_SESSION, message=msg
            )

        self.logging("Login error toast not found. Verifying page loaded.", "INFO")
        main_page_content = browser_port.is_visible(selectors.main_page_container, 5000)
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

    def check_shutdown(self, should_stop_cb: Callable):
        if should_stop_cb():
            raise Exception
