from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...auth.session.session_registry import SessionRegistry
    from ...auth.enums import PROVIDERS

    from services.logger.adapters import LogAdapter
    from services.browser.ports import BrowserPort
    from ..models.intra_login import IntraLogin
    from services.profiles import ProfileRegistry
    from services.profiles.models import LoginSelectors

import time

from playwright.sync_api import Error as PlaywrightError, TimeoutError

from ...auth.base_auth_service import BaseAuthService
from ...auth.enums.auth_status import AUTHSTATUS
from ...auth.models.auth_result import AuthResult
from ...auth.models.auth_validation_response import AuthValidationResponse


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
            try:
                token = browser_port.capture_response_json(
                    url_contains="openid-connect/token",
                    action=lambda: self._enter_login_info(
                        creds, browser_port, selectors
                    ),
                    method="POST",
                    timeout=5_000,
                )
                print("here is the token response")
                print(token)
            except TimeoutError as _:
                msg = "Error during login. Couldnt log in."
                self.logging(msg, "ERROR")
                error_toast = browser_port.is_visible(selectors.error_container, 3000)
                if error_toast:
                    msg = "Invalid User Credentials, Please check your Username or Password."
                    self.logging(msg, "ERROR")
                    return AuthResult(
                        success=False,
                        status=AUTHSTATUS.INVALID_CREDENTIALS,
                        message=msg,
                    )
                return AuthResult(
                    success=False, status=AUTHSTATUS.BROWSER_ERROR, message=msg
                )

            self.check_shutdown(should_stop_cb)
            browser_port.wait_for_page_ready()
            self.check_shutdown(should_stop_cb)
            msg = "Found Session Token. Login Successful."
            self.logging(msg)
            return AuthResult(success=True, status=AUTHSTATUS.SUCCESS, message=msg)
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
        browser_port.click(selectors.submit_button, timeout=5000)

    def check_shutdown(self, should_stop_cb: Callable):
        if should_stop_cb():
            raise Exception
