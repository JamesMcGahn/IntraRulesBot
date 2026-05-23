from services.browser.ports.browser_port import BrowserPort


from playwright.sync_api import (
    Page,
    FrameLocator,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

from .playwright_interaction_adapter import PlaywrightInteractionAdapter


class PlaywrightBrowserAdapter(BrowserPort):

    def __init__(self, page: Page):
        self._page = page
        self.interactions = PlaywrightInteractionAdapter(page)

    def goto(self, url: str) -> None:
        self._page.goto(url)

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

    def click_and_accept_alert_if_appears(
        self,
        locator: str,
        check_alert_text: str | None = None,
        timeout: int = 3000,
    ) -> bool:
        try:
            with self._page.expect_event("dialog", timeout=timeout) as dialog_info:
                self._page.locator(locator).click()

            dialog = dialog_info.value
            message = dialog.message

            if check_alert_text and check_alert_text not in message:
                dialog.dismiss()
                return False

            dialog.accept()
            return True

        except PlaywrightTimeoutError:
            return False

        except PlaywrightError as e:
            return False

    def frame_click_and_accept_alert_if_appears(
        self,
        frame_locator: FrameLocator,
        click_selector: str,
        check_alert_text: str | None = None,
        timeout: int = 3000,
    ) -> bool:
        try:
            with self._page.expect_event("dialog", timeout=timeout) as dialog_info:
                frame_locator.locator(click_selector).click()

            dialog = dialog_info.value
            message = dialog.message

            if check_alert_text and check_alert_text not in message:
                dialog.dismiss()
                return False

            dialog.accept()
            return True

        except PlaywrightTimeoutError:
            return False

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
