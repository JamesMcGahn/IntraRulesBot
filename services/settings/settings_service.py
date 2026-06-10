from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .settings_repository import SettingsRepository
    from .models import SettingUpdatedPayload, SettingValidatedPayload
    from services.logger.adapters import LogAdapter
from copy import deepcopy

from PySide6.QtCore import Slot

from base import QObjectBase

from .enums import SETTINGSCATEGORIES
from .models import AppSettings
from .models.base_category_map import SettingsCategoryBase
from .models.map_app_settings import AppSettings as AppSettingsMap
from .models.map_log_settings import LogSettings
from .models.map_login_settings import LoginSettings


class SettingsService(QObjectBase):

    def __init__(self, logger: LogAdapter, repo: SettingsRepository):
        super().__init__(logger)
        self._repo = repo
        self._settings: AppSettingsMap = None
        self._validated: dict[SETTINGSCATEGORIES, dict[str, bool]] = {}
        self.sections: dict[SETTINGSCATEGORIES, SettingsCategoryBase] = {
            SETTINGSCATEGORIES.LOGIN: LoginSettings,
            SETTINGSCATEGORIES.LOG: LogSettings,
        }
        self._settings_loaded = False

        self.load_settings()

    def load_settings(self):
        if self._settings_loaded:
            return

        self._settings = AppSettings()
        self._validated = {}
        self._logging("Loading Settings from Repository")
        for category, dc in self.sections.items():
            self._logging(f"Loading {dc} settings.", "DEBUG")
            cat_settings, validated = self._repo.load_section(dc)
            attr = category.value
            setattr(self._settings, attr, cat_settings)
            self._validated[category] = validated
        self._logging("Successfully Loaded Settings from Repository")
        self._settings_loaded = True

    @Slot()
    def save_settings(self):
        self._logging("Saving Settings.")
        for category, dc in self.sections.items():
            validated = self._validated.get(category, {})
            self._logging(f"Saving {dc} settings.", "DEBUG")
            section = getattr(self._settings, category)
            self._repo.save_section(section, validated)
        self._logging("Settings save sucessfully.")

    def get_settings(self) -> AppSettingsMap:
        return deepcopy(self._settings)

    def get_validations(self) -> dict[SETTINGSCATEGORIES, dict[str, bool]]:
        return deepcopy(self._validated)

    def update_setting(self, event: SettingUpdatedPayload):
        section = getattr(self._settings, event.category, None)
        if section is None:
            msg = "{event.category} does not exist"
            self._logging(msg, "ERROR")
            raise ValueError(msg)
        setattr(section, event.field, event.value)
        self._validated.setdefault(event.category, {})
        self._validated[event.category][event.field] = False

    def set_validated(self, payload: SettingValidatedPayload):
        self._validated.setdefault(payload.category, {})[
            payload.field
        ] = payload.is_valid

    def is_validated(self, section: str, field: str) -> bool:
        return self._validated.get(section, {}).get(field, False)

    def get_category(self, category: SETTINGSCATEGORIES) -> SettingsCategoryBase:
        # attr = category.value
        cat = getattr(self._settings, category, None)
        if not cat:
            msg = f"Cannot Find Category: {category}"
            self._logging(msg)
            raise ValueError(msg)
        return cat

    def get_category_validation(self, category: SETTINGSCATEGORIES) -> dict[str, bool]:
        cat = self._validated.get(category)
        if not cat:
            msg = f"Cannot Find Category: {category}"
            self._logging(msg)
            raise ValueError(msg)
        return cat

    def get_field_meta(self, category: SETTINGSCATEGORIES, field: str):
        field_category = self.get_category(category)
        meta = field_category.get_field_meta(field)
        if not meta:
            msg = f"Cannot find {field} in {category} meta dictionary"
            self._logging(msg, "ERROR")
            raise ValueError(msg)
        return meta
