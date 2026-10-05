from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import StartUpContainer
import subprocess


from utils.files import PathManager
from services.auth.enums import PROVIDERS
from PySide6.QtCore import QObject, Signal
from playwright._impl._driver import compute_driver_executable, get_driver_env
from services.settings.enums import SETTINGSCATEGORIES
from base.enums import INTRAVERSION


class StartUpCoordinator(QObject):
    done = Signal(bool)
    start_service = Signal()

    def __init__(self, container: StartUpContainer):
        super().__init__()
        self.container = container
        self.logger = self.container.logger
        self.start_service.connect(self.container.intra_token_service.start_service)

    def _logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def run_start_checks(self):
        try:
            self._logging("Starting Start Up Checks....", "INFO")
            self.container.rule_sets_controller.load_editor_state()
            self.container.rules_controller.load_editor_state()
            self.container.session_registry.pre_load_providers(
                [PROVIDERS.INTRA_V10, PROVIDERS.INTRA_V11]
            )
            self.container.profiles_controller.load_profiles()
            self.container.profiles_controller.save_profiles()
            self.set_current_provider()
            self.start_service.emit()
            self.ensure_playwright_browsers()
            self._logging("Starting Start Up Checks Finished.", "INFO")
            self.done.emit(True)
        except Exception:
            self.done.emit(False)

    def set_current_provider(self):
        login_settings = self.container.settings_manager.get_category(
            SETTINGSCATEGORIES.LOGIN
        )
        if INTRAVERSION.V11 == login_settings.platform_version:
            self.container.session_registry.set_current_session(PROVIDERS.INTRA_V11)
        else:
            self.container.session_registry.set_current_session(PROVIDERS.INTRA_V10)

    def ensure_playwright_browsers(self):
        folder = PathManager.create_folder_in_app_data("playwright")
        env = get_driver_env()
        env["PLAYWRIGHT_BROWSERS_PATH"] = folder
        self._logging(
            "Ensuring Playwright is installed. ** This can take a while. **",
            "INFO",
        )
        node_executable, cli_path = compute_driver_executable()
        command = [
            node_executable,
            cli_path,
            "install",
            "chromium",
        ]

        try:
            result = subprocess.run(
                command,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            if result.stdout:

                self._logging(
                    f"Playwright install output:\n{result.stdout}",
                    "INFO",
                )

            if result.stderr:

                self._logging(
                    f"Playwright install error output:\n{result.stderr}",
                    "WARN",
                )

            self._logging(
                "Playwright Chromium is ready.",
                "INFO",
            )
        except subprocess.CalledProcessError as e:

            if e.stdout:

                self._logging(
                    f"Playwright install stdout before failure:\n{e.stdout}",
                    "ERROR",
                )

            if e.stderr:

                self._logging(
                    f"Playwright install stderr before failure:\n{e.stderr}",
                    "ERROR",
                )

            self._logging(
                f"Playwright browser install failed with exit code {e.returncode}.",
                "ERROR",
            )
            raise
        except Exception as e:

            self._logging(
                f"Playwright browser install failed: {e}.",
                "ERROR",
            )
            raise
