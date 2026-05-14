from services.browser.ports.frame_port import FramePort


from playwright.sync_api import FrameLocator, Locator

from .playwright_interaction_adapter import PlaywrightInteractionAdapter


class PlaywrightFrameLocatorAdapter(FramePort):

    def __init__(self, frame_locator: FrameLocator):
        self._frame_locator = frame_locator
        self.interactions = PlaywrightInteractionAdapter(frame_locator)

    def frame_locator(self, selector: str) -> FramePort:
        frame = self._frame_locator.frame_locator(selector)
        if frame is None:
            raise ValueError(f"Frame not found: {selector}")

        return PlaywrightFrameLocatorAdapter(frame)

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
