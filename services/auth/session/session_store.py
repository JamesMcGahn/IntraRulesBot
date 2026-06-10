from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...logger.adapters import LogAdapter
    from ...files import JSONFileService

from utils.files import PathManager
from pathlib import Path
from ..models.provider_session_data import ProviderSessionData


class SessionStore:

    def __init__(self, json_file_service: JSONFileService, logger: LogAdapter):
        super().__init__()
        self._logger = logger
        self.json_file_service = json_file_service

    def _logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}{msg}"
        self._logger(msg, level, print_msg)

    def save_cookies(self, provider_name: str, cookies: list[dict]) -> None:
        if not cookies:
            return
        self._logging(f"({provider_name.upper()}): saving cookies...", "INFO")
        path = PathManager.create_folder_in_app_data(f"session/{provider_name}")
        res = self.json_file_service.save(cookies, Path(path) / "session.json")
        if res.ok:
            self._logging(
                f"({provider_name.upper()}): cookies saved successfully.", "INFO"
            )
        else:
            self._logging(f"({provider_name.upper()}): cookies failed to save.", "INFO")

    def save_token(self, provider_name: str, token: str) -> None:
        if token is None:
            self._logging(
                f"({provider_name.upper()}): skipping saving token. Token is None.",
                "INFO",
            )
            return

        self._logging(f"({provider_name.upper()}): saving token...", "INFO")
        path = PathManager.create_folder_in_app_data(f"session/{provider_name}")

        res = self.json_file_service.save({"token": token}, Path(path) / "token.json")
        if res.ok:
            self._logging(
                f"({provider_name.upper()}): token saved successfully.", "INFO"
            )
        else:
            self._logging(f"({provider_name.upper()}): token failed to save.", "WARN")

    def load_token(self, provider_name: str) -> str | None:
        self._logging(
            f"({provider_name.upper()}): checking for a stored token.", "INFO"
        )
        path = PathManager.create_folder_in_app_data(f"session/{provider_name}")
        file = Path(path) / "token.json"
        token = None
        res = self.json_file_service.load(file)

        if res.ok and res.data.get("token"):
            self._logging(
                f"({provider_name.upper()}): Token Loaded Successfully...", "INFO"
            )
            return token["token"]
        else:
            self._logging(f"({provider_name.upper()}): No Token Found", "WARN")
            return None

    def load_cookies(self, provider_name: str) -> list[dict]:
        self._logging(
            f"({provider_name.upper()}): Trying to Load Cookies From File", "INFO"
        )
        path = PathManager.create_folder_in_app_data(f"session/{provider_name}")
        file = Path(path) / "session.json"
        res = self.json_file_service.load(file)
        if res.ok:
            self._logging(
                f"({provider_name.upper()}): Session Loaded Successfully...", "INFO"
            )
            return res.data

        return []

    def load_session(
        self,
        provider_name: str,
        has_token: bool,
        has_cookies: bool,
    ) -> ProviderSessionData:
        token = None
        cookies = []
        if has_token:
            token = self.load_token(provider_name)
        if has_cookies:
            cookies = self.load_cookies(provider_name)
        return ProviderSessionData(cookies, token)

    def save_session(
        self,
        provider_name: str,
        provider_data: ProviderSessionData,
        has_token: bool,
        has_cookies: bool,
    ) -> None:
        if has_token:
            self.save_token(provider_name, provider_data.token)
        if has_cookies:
            self.save_cookies(provider_name, provider_data.cookies)
