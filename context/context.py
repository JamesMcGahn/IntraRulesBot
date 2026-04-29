import os
import subprocess
import sys

import requests
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, QSingleton

from utils.files import PathManager

from services.logger import Logger
from services.settings import (
    AppSettings,
    SecureCredentials,
    SettingsRepository,
    SettingsService,
)
from services.settings.enums import SETTINGSCATEGORIES
from services.validation import ValidationService
from controllers import SettingsController, RulesController

from schemas.registry import SchemaRegistry


class AppContext(QObjectBase, metaclass=QSingleton):
    appshutdown = Signal()
    setting_updated = Signal(object)

    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.settings = AppSettings()
        self.secure_settings = SecureCredentials()
        self.settings_repo = SettingsRepository(self.settings, self.secure_settings)
        self.settings_manager = SettingsService(repo=self.settings_repo)

        self.schema_registry = SchemaRegistry()

        self.validation_service = ValidationService(
            settings_meta_provider=self.settings_manager,
            schema_meta_provider=self.schema_registry,
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
            validation_service=self.validation_service
        )

        folder = PathManager.create_folder_in_app_data("playwright")
        self.ensure_playwright_browsers(folder)

        self.appshutdown.connect(self.settings_manager.save_settings)

        # CONNECTIONS
        ## SETTINGS
        self.settings_controller.setting_updated.connect(self.setting_updated)
        self.setting_updated.connect(self.logger.received_settings_change)

    def ensure_playwright_browsers(self, app_data_path):
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = app_data_path

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            env=env,
            check=True,
        )
