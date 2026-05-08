from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .session.session_registry import SessionRegistry
    from .models.auth_result import AuthResult
    from services.logger.adapters import LogAdapter
    from services.rule_runner.interfaces import BrowserPort


from .enums import PROVIDERS
from .models import AuthValidationResponse

from ..intra.intra_auth_service import IntraAuthService
from .session.session_registry import SessionRegistry
from .base_auth_service import BaseAuthService


class AuthService:

    def __init__(self, session_registry: SessionRegistry, logger: LogAdapter):
        super().__init__()
        self._providers: dict[PROVIDERS, BaseAuthService] = {
            PROVIDERS.INTRA: IntraAuthService(
                session_registry, PROVIDERS.INTRA, logger
            ),
        }

    def validate(self, provider: PROVIDERS) -> AuthValidationResponse:
        service = self._providers.get(provider)
        if not service:
            raise NotImplementedError(f"{provider} not implemented")
        return service.validate()

    def ensure_auth(
        self,
        provider: PROVIDERS,
        creds,
        browser_port: BrowserPort | None = None,
        force_login: bool = True,
        should_stop_cb: Callable[[], bool] | None = None,
    ) -> AuthResult:
        service = self._providers.get(provider)
        if not service:
            raise NotImplementedError(f"{provider} not implemented")
        return service.ensure_auth(creds, browser_port, force_login, should_stop_cb)

    def can_attempt_login(self, provider) -> bool:
        service = self._providers.get(provider)
        if not service:
            raise NotImplementedError(f"{provider} not implemented")
        return service.can_attempt_login()
