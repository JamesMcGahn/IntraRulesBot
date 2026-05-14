from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.session import SessionRegistry
    from services.auth.enums import PROVIDERS
    from services.logger.adapters import LogAdapter

from .play_wright_session_manager import PlaywrightSessionManager


class BrowserSessionFactory:

    def __init__(self, session_registry: SessionRegistry, logger: LogAdapter):
        self.session_registry = session_registry
        self.logger = logger

    def create_session(
        self,
        provider: PROVIDERS,
    ) -> PlaywrightSessionManager:

        return PlaywrightSessionManager(
            provider_session=self.session_registry.for_provider(provider),
            logger=self.logger,
        )
