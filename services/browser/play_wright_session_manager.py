from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.auth.session import BaseProviderSession
    from services.logger.adapters import LogAdapter

import os

from playwright.sync_api import sync_playwright
from .models import PlaywrightSession
from .adapters import PlaywrightBrowserAdapter


class PlaywrightSessionManager:

    def __init__(self, provider_session: BaseProviderSession, logger: LogAdapter):
        self.provider_session = provider_session
        self.logger = logger
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        from utils.files import PathManager

        app_data_playwright_path = PathManager.create_folder_in_app_data("playwright")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = app_data_playwright_path

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)

    def start(self) -> PlaywrightSession:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, slow_mo=1000)
        self.context = self.browser.new_context()

        cookies = self.provider_session.convert_jar_to_cookie_list()
        if cookies:
            self.context.add_cookies(cookies)

        self.page = self.context.new_page()

        return PlaywrightSession(
            browser_adapter=PlaywrightBrowserAdapter(self.page),
            page=self.page,
            context=self.context,
        )

    def save_cookies(self) -> None:
        if not self.context:
            return

        cookies = self.context.cookies()
        self.provider_session.update_cookies_from_list(cookies)
        self.provider_session.save_session()

    def close(self) -> None:
        self.save_cookies()

        if self.context:
            self.context.close()

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()
