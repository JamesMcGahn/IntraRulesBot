import os
import subprocess
import sys

import requests
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, QSingleton

from utils.files import PathManager


class AppContext(QObjectBase, metaclass=QSingleton):
    appshutdown = Signal()

    def __init__(self):
        super().__init__()

        folder = PathManager.create_folder_in_app_data("playwright")
        self.ensure_playwright_browsers(folder)

    def ensure_playwright_browsers(self, app_data_path):
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = app_data_path

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            env=env,
            check=True,
        )
