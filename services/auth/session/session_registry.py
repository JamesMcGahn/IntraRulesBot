from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...logger.adapters import LogAdapter


from ..enums import PROVIDERS
from .base_provider_session import BaseProviderSession
from services.intra.intra_provider_session import IntraProviderSession


class SessionRegistry:

    def __init__(self, logger: LogAdapter):
        super().__init__()
        self.logger = logger
        self._sessions: dict[PROVIDERS, BaseProviderSession] = {}

        self.providers = {
            PROVIDERS.INTRA: IntraProviderSession,
        }

    def for_provider(self, provider: PROVIDERS) -> BaseProviderSession:
        if provider not in self._sessions:
            provider_session = self.providers.get(provider, BaseProviderSession)
            session = provider_session(self.logger)
            session.load_session()
            self._sessions[provider] = session
        return self._sessions[provider]

    def pre_load_providers(self, providers: list[PROVIDERS]):
        for provider in providers:
            self.for_provider(provider)

    def save_all(self):
        for provider_session in self._sessions.values():
            provider_session.save_session()
