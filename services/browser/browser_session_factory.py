from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.session import SessionRegistry
    from services.auth.enums import PROVIDERS
    from services.logger.adapters import LogAdapter
from .models import PlaywrightConfig

from .play_wright_session_manager import PlaywrightSessionManager


class BrowserSessionFactory:

    def __init__(self, session_registry: SessionRegistry, logger: LogAdapter):
        self.session_registry = session_registry
        self.logger = logger

        self.config = PlaywrightConfig()

    def create_session(
        self, provider: PROVIDERS, config: PlaywrightConfig | None = None
    ) -> PlaywrightSessionManager:
        if config is None:
            config = self.config
        return PlaywrightSessionManager(
            provider_session=self.session_registry.for_provider(provider),
            logger=self.logger,
            config=config,
        )
