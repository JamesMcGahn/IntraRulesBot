from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import StartUpContainer
import os
import subprocess
import sys

from utils.files import PathManager
from services.auth.enums import PROVIDERS
from PySide6.QtCore import QObject, Signal


class StartUpCoordinator(QObject):
    done = Signal(bool)

    def __init__(self, container: StartUpContainer):
        super().__init__()
        self.container = container
        self.logger = self.container.logger

    def _logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def run_start_checks(self):
        try:
            self._logging("Starting Start Up Checks....", "INFO")
            self.container.rule_sets_controller.load_editor_state()
            self.container.rules_controller.load_editor_state()
            self.container.session_registry.pre_load_providers([PROVIDERS.INTRA])
            self.ensure_playwright_browsers()
            self._logging("Starting Start Up Checks Finished.", "INFO")
            self.done.emit(True)
        except Exception:
            self.done.emit(False)

    def ensure_playwright_browsers(self):
        folder = PathManager.create_folder_in_app_data("playwright")
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = folder
        self._logging(
            "Ensuring Playwright is installed. ** This can take a while. **",
            "INFO",
        )
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
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
