from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .session.session_registry import SessionRegistry
    from .enums import PROVIDERS
    from .models.auth_result import AuthResult
    from services.logger.adapters import LogAdapter
    from services.rule_runner.interfaces import BrowserPort

import time

from .models.auth_validation_response import AuthValidationResponse


class BaseAuthService:

    def __init__(
        self, session_registry: SessionRegistry, provider: PROVIDERS, logger: LogAdapter
    ):
        self.logger = logger
        self.session = session_registry.for_provider(provider=provider)
        self.provider_name = provider
        self.last_login_attempt = None
        self.login_cooldown_seconds = self.session.login_cool_down

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def validate(self) -> AuthValidationResponse:
        raise NotImplementedError

    def ensure_auth(self, creds, browser_port: BrowserPort | None = None) -> AuthResult:
        raise NotImplementedError

    def can_attempt_login(self) -> bool:
        if not self.last_login_attempt:
            return True

        elapsed = time.time() - self.last_login_attempt
        return elapsed > self.login_cooldown_seconds
