from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..settings_service import SettingsService
    from ..models.map_login_settings import LoginSettings

from ..enums import SETTINGSCATEGORIES
from ...rule_runner.models import RuleRunnerConfig


class SettingsRuleRunnerConfigProvider:

    def __init__(self, settings_service: SettingsService):
        self._settings_service = settings_service

    def get_rule_run_config(self) -> RuleRunnerConfig:
        login: LoginSettings = self._settings_service.get_category(
            SETTINGSCATEGORIES.LOGIN
        )

        return RuleRunnerConfig(
            user_name=login.user_name,
            password=login.password,
            tenant=login.tenant,
            platform_version=login.platform_version,
        )
