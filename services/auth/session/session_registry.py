from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...logger.adapters import LogAdapter
    from .session_store import SessionStore

from ..enums import PROVIDERS
from .base_provider_session import BaseProviderSession
from services.intra.intra_provider_session import IntraProviderSession


class SessionRegistry:

    def __init__(
        self,
        session_store: SessionStore,
        logger: LogAdapter,
    ):
        super().__init__()
        self.logger = logger
        self.session_store = session_store
        self._sessions: dict[PROVIDERS, BaseProviderSession] = {}

        self.providers = {
            PROVIDERS.INTRA: IntraProviderSession,
        }

    def for_provider(self, provider: PROVIDERS) -> BaseProviderSession:
        if provider not in self._sessions:
            provider_session = self.providers.get(provider, BaseProviderSession)
            session = provider_session(self.logger)
            session_data = self.session_store.load_session(
                provider, session.has_token, session.has_cookies
            )
            session.hydrate(session_data)
            self._sessions[provider] = session
        return self._sessions[provider]

    def pre_load_providers(self, providers: list[PROVIDERS]):
        for provider in providers:
            self.for_provider(provider)

    def save_all(self):
        for provider_session in self._sessions.values():
            snapshot = provider_session.session_snapshot()
            self.session_store.save_session(
                provider_session.provider_name,
                snapshot,
                provider_session.has_token,
                provider_session.has_cookies,
            )
