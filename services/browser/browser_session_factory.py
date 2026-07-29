from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.session import SessionRegistry
    from services.auth.enums import PROVIDERS
    from services.logger.adapters import LogAdapter
    from ..settings.events import SettingUpdatedEvent
from .models import PlaywrightConfig
from PySide6.QtCore import QObject, Slot
from .play_wright_session_manager import PlaywrightSessionManager
from ..settings.enums import SETTINGSCATEGORIES
from services.settings.models import BrowserSettings


class BrowserSessionFactory(QObject):

    def __init__(self, session_registry: SessionRegistry, logger: LogAdapter):
        self.session_registry = session_registry
        self.logger = logger
        self._settings_loaded = False
        self.browser_headless = False
        self.browser_move_delay_speed = 500

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

    def load_settings(self, settings: BrowserSettings):
        if self._settings_loaded:
            return
        for field in settings.get_fields_list():
            value = getattr(settings, field.name, None)
            setattr(self, field.name, value)
        self._settings_loaded = True

    def _update_config(self):
        self.config = PlaywrightConfig(
            headless=bool(self.browser_headless), slow_mo=self.browser_move_delay_speed
        )

    @Slot(object)
    def received_settings_change(self, event: SettingUpdatedEvent):
        if event.category != SETTINGSCATEGORIES.BROWSER:
            return
        if not hasattr(self, event.field):
            raise ValueError(f"{event.field} not defined in class")
        setattr(self, event.field, event.value)

        self._update_config()
        self.logger(
            "Browser Settings changed. Settings will apply to the next Browser Session.",
            "INFO",
            True,
        )
