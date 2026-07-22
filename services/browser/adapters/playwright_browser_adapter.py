from playwright.sync_api import (
    Dialog,
    FrameLocator,
    Locator,
    Page,
)
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from services.browser.ports.browser_port import BrowserPort

from .playwright_interaction_adapter import PlaywrightInteractionAdapter


class PlaywrightBrowserAdapter(BrowserPort):

    def __init__(self, page: Page):
        self._page = page
        self.interactions = PlaywrightInteractionAdapter(page)

    def goto(self, url: str) -> None:
        self._page.goto(url)

    def is_current_url(
        self, url_part: str, exact: bool = False, case_sensitive: bool = False
    ) -> bool:

        current_url = self._page.url
        if not case_sensitive:
            current_url = current_url.lower()
            url_part = url_part.lower()

        if exact:
            return current_url == url_part

        return url_part in current_url

    def frame_locator(self, selector: str) -> PlaywrightInteractionAdapter:
        frame = self._page.frame_locator(selector)
        if frame is None:
            raise ValueError(f"Frame not found: {selector}")

        return PlaywrightInteractionAdapter(frame)

    def click(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None:
        return self.interactions.click(selector, timeout)

    def fill(
        self,
        selector: str,
        text: str,
        timeout: int = 30000,
    ) -> None:
        return self.interactions.fill(selector, text, timeout)

    def text_content(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> str:
        return self.interactions.text_content(selector, timeout)

    def exists(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> bool:
        return self.interactions.exists(selector, timeout)

    def is_visible(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> bool:
        return self.interactions.is_visible(selector, timeout)

    def wait_visible(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None:
        return self.interactions.wait_visible(selector, timeout)

    def locator(self, selector: str) -> Locator:
        return self.interactions.locator(selector)

    def screenshot(self, path: str) -> None:
        self._page.screenshot(path=path)

    def _handle_dialog(
        self, dialog: Dialog, check_alert_text: str, result: dict[str, bool]
    ):
        message = dialog.message
        if check_alert_text and check_alert_text not in message:
            dialog.dismiss()
            result["result"] = False
            return

        dialog.accept()
        result["result"] = True

    def click_and_accept_alert_if_appears(
        self,
        selector: str,
        check_alert_text: str | None = None,
        timeout: int = 3000,
        click_timeout: int = 60000,
    ) -> bool:
        result = {"result": False}

        def handler(dialog: Dialog) -> None:
            self._handle_dialog(dialog, check_alert_text, result)

        self._page.on("dialog", handler)

        try:
            self._page.locator(selector).click(timeout=click_timeout)
            self._page.wait_for_timeout(timeout)
            return result["result"]
        finally:
            self._page.remove_listener("dialog", handler)

    def frame_select_from_list_and_accept_alert_if_appears(
        self,
        frame_locator: FrameLocator,
        list_selector: str,
        text_to_select: str,
        check_alert_text: str | None = None,
        timeout: int = 3000,
    ) -> bool:
        result = {
            "appeared": False,
            "accepted": False,
            "message": None,
        }

        def handle_dialog(dialog: Dialog) -> None:
            result["appeared"] = True
            result["message"] = dialog.message

            if check_alert_text and check_alert_text not in dialog.message:
                dialog.dismiss()
                return

            dialog.accept()
            result["accepted"] = True

        self._page.on("dialog", handle_dialog)

        try:
            adapter = PlaywrightInteractionAdapter(frame_locator)
            adapter.select_exact_item_from_list(
                list_selector,
                text_to_select,
            )

            if not result["appeared"] and timeout > 0:
                self._page.wait_for_timeout(timeout)

            return result["accepted"]

        finally:
            self._page.remove_listener("dialog", handle_dialog)

    def frame_click_and_accept_alert_if_appears(
        self,
        frame_locator: FrameLocator,
        click_selector: str,
        check_alert_text: str | None = None,
        timeout: int = 3000,
    ) -> bool:
        result = {"result": False}

        def handler(dialog: Dialog) -> None:
            self._handle_dialog(dialog, check_alert_text, result)

        self._page.on("dialog", handler)

        try:
            frame_locator.locator(click_selector).click()
            self._page.wait_for_timeout(timeout)
            return result["result"]
        finally:
            self._page.remove_listener("dialog", handler)

    def wait_for_page_ready(self, timeout: int = 30000) -> None:
        self._page.wait_for_load_state("domcontentloaded", timeout=timeout)

    def select_item_from_list(
        self, selector: str, text_to_select: str | int, timeout: int = 30000
    ) -> None:
        return self.interactions.select_item_from_list(
            selector, text_to_select, timeout
        )

    def select_exact_item_from_list(
        self, selector: str, text_to_select: str | int, timeout: int = 30000
    ) -> None:
        return self.interactions.select_exact_item_from_list(
            selector, text_to_select, timeout
        )

    def click_all_items_in_list(self, selector: str, timeout: int = 30000) -> None:
        return self.interactions.click_all_items_in_list(selector, timeout)

    def find_by_has_text(
        self,
        base_selector: str,
        has_selector: str,
        text: str,
        strict_exact: bool = False,
    ) -> Locator:
        return self.interactions.find_by_has_text(
            base_selector, has_selector, text, strict_exact
        )

    def find_child_by_has_text(
        self,
        parent: Locator,
        base_selector: str,
        has_selector: str,
        text: str,
        strict_exact: bool = False,
    ) -> Locator:
        return self.interactions.find_child_by_has_text(
            parent, base_selector, has_selector, text, strict_exact
        )

    def click_inside_parent(
        self,
        parent: Locator,
        selector: str,
        timeout: int = 30000,
        no_wait_after: bool = False,
    ) -> None:
        return self.interactions.click_inside_parent(
            parent, selector, timeout, no_wait_after
        )

    def wait_for_locator_visible(
        self,
        locator: Locator,
        timeout: int = 30000,
    ) -> None:
        return self.interactions.wait_for_locator_visible(locator, timeout)
