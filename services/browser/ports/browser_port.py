from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from playwright.sync_api import FrameLocator
from .interaction_port import InteractionPort


class BrowserPort(InteractionPort, Protocol):

    def goto(self, url: str) -> None: ...

    def frame_locator(selector: str) -> InteractionPort: ...

    def screenshot(self, path: str) -> None: ...

    def click_and_accept_alert_if_appears(
        self,
        locator: str,
        check_alert_text: str | None = None,
        timeout: int = 3000,
    ) -> bool: ...

    def frame_click_and_accept_alert_if_appears(
        self,
        frame_locator: FrameLocator,
        click_selector: str,
        check_alert_text: str | None = None,
        timeout: int = 3000,
    ) -> bool: ...

    def wait_for_page_ready(self, timeout: int = 30000) -> None: ...
