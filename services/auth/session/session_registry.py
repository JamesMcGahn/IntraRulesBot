from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...logger.adapters import LogAdapter
    from .session_store import SessionStore
    from services.settings.events import SettingUpdatedEvent

from PySide6.QtCore import QObject, Slot
from ..enums import PROVIDERS
from services.auth.session.base_provider_session import BaseProviderSession
from services.intra.v10.intra_provider_session import IntraProviderSession as IntraV10
from services.intra.v11.intra_provider_session import IntraProviderSession as IntraV11
from services.settings.enums import SETTINGSCATEGORIES
from base.enums import INTRAVERSION
from base.logging_base import LoggingBase


class SessionRegistry(QObject, LoggingBase):

    def __init__(
        self,
        session_store: SessionStore,
        logger: LogAdapter,
    ):
        super().__init__(logger=logger)
        self.logger = logger
        self.session_store = session_store
        self._sessions: dict[PROVIDERS, BaseProviderSession] = {}
        self._current_session: BaseProviderSession = BaseProviderSession
        self.providers = {PROVIDERS.INTRA_V10: IntraV10, PROVIDERS.INTRA_V11: IntraV11}

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

    def current_session(self) -> BaseProviderSession:
        return self._current_session

    def pre_load_providers(self, providers: list[PROVIDERS]):
        for provider in providers:
            self.for_provider(provider)

    @Slot(object)
    def received_settings_change(self, event: SettingUpdatedEvent):
        if event.category != SETTINGSCATEGORIES.LOGIN:
            return
        if event.field != "platform_version":
            return
        version = INTRAVERSION(event.value)
        provider_mapping = {
            INTRAVERSION.V10: PROVIDERS.INTRA_V10,
            INTRAVERSION.V11: PROVIDERS.INTRA_V11,
        }

        self._current_session = provider_mapping.get(version, BaseProviderSession)
        self.logging(f"Setting current session to {self._current_session}")

    def save_all(self):
        self.logging("Saving all sessions...")
        for provider_session in self._sessions.values():
            snapshot = provider_session.session_snapshot()
            self.session_store.save_session(
                provider_session.provider_name,
                snapshot,
                provider_session.has_token,
                provider_session.has_cookies,
            )
