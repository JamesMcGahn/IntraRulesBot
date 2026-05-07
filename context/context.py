import os
import subprocess
import sys

from PySide6.QtCore import Signal, QObject

from base import QSingleton

from utils.files import PathManager

from services.logger import Logger
from services.settings import (
    AppSettings,
    SecureCredentials,
    SettingsRepository,
    SettingsService,
)
from services.settings.providers import SettingsRuleRunnerConfigProvider
from services.settings.enums import SETTINGSCATEGORIES
from services.validation import ValidationService
from controllers import SettingsController, RulesController
from services.rules import RuleRegistry, RuleStore, RuleBuilder
from schemas.registry import SchemaRegistry
from services.rule_runner import RuleRunnerService
from services.auth.session import SessionRegistry
from services.auth.auth_service import AuthService
from services.auth.enums import PROVIDERS
from services.logger.adapters import LogAdapter


class AppContext(QObject, metaclass=QSingleton):
    app_shut_down_confirmed = Signal()
    setting_updated = Signal(object)
    send_logs = Signal(str, str, bool)

    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.send_logs.connect(self.logger.insert)
        self.log_adapter = LogAdapter(self.logger)
        self.settings = AppSettings()
        self.secure_settings = SecureCredentials()
        self.settings_repo = SettingsRepository(self.settings, self.secure_settings)
        self.settings_manager = SettingsService(repo=self.settings_repo)
        self.session_registry = SessionRegistry(self.log_adapter)
        self.auth_service = AuthService(self.session_registry, self.log_adapter)

        self.schema_registry = SchemaRegistry()
        self.rules_registry = RuleRegistry()
        self.rule_store = RuleStore()
        self.rule_builder = RuleBuilder()

        self.validation_service = ValidationService(
            settings_meta_provider=self.settings_manager,
            schema_meta_provider=self.schema_registry,
        )
        self.rule_settings_provider = SettingsRuleRunnerConfigProvider(
            settings_service=self.settings_manager
        )
        self.rule_runner_service = RuleRunnerService(
            settings_provider=self.rule_settings_provider,
            session=self.session_registry.for_provider(PROVIDERS.INTRA),
            auth_service=self.auth_service,
        )
        log_settings = self.settings_manager.get_category(SETTINGSCATEGORIES.LOG)
        self.logger.load_settings(log_settings)
        self.logger.start_up()

        ## Controllers
        self.settings_controller = SettingsController(
            settings_service=self.settings_manager,
            validation_service=self.validation_service,
        )
        self.rules_controller = RulesController(
            validation_service=self.validation_service,
            rules_registry=self.rules_registry,
            rule_store=self.rule_store,
            rule_builder=self.rule_builder,
            rule_runner_service=self.rule_runner_service,
        )

        folder = PathManager.create_folder_in_app_data("playwright")
        self.rules_controller.load_editor_state()
        self.ensure_playwright_browsers(folder)
        self.session_registry.pre_load_providers([PROVIDERS.INTRA])

        # CONNECTIONS
        ## SETTINGS
        self.settings_controller.setting_updated.connect(self.setting_updated)
        self.setting_updated.connect(self.logger.received_settings_change)
        self.session_registry.save_all()

    def ensure_playwright_browsers(self, app_data_path):
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = app_data_path

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            env=env,
            check=True,
        )

    ## App shutdown
    def handle_app_shut_down(self):
        self.logger.close()
        self.settings_manager.save_settings()
        self.session_registry.save_all()
        self.app_shut_down_confirmed.emit()
