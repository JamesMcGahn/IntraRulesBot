from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..settings_service import SettingsService
    from ..models.map_login_settings import LoginSettings

from ..enums import SETTINGSCATEGORIES
from ...queue_runner.models import QueueRunnerConfig


class SettingsQueueRunnerConfigProvider:

    def __init__(self, settings_service: SettingsService):
        self._settings_service = settings_service

    def get_queue_run_config(self) -> QueueRunnerConfig:
        login: LoginSettings = self._settings_service.get_category(
            SETTINGSCATEGORIES.LOGIN
        )
        valid_dict = self._settings_service.get_category_validation(
            SETTINGSCATEGORIES.LOGIN
        )
        is_valid = all(valid_dict.values())
        return QueueRunnerConfig(
            user_name=login.user_name,
            password=login.password,
            tenant=login.tenant,
            platform_version=login.platform_version,
            login_valid=is_valid,
        )
