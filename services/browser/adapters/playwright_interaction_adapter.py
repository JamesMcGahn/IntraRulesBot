from __future__ import annotations


from playwright.sync_api import (
    Page,
    FrameLocator,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
)


class PlaywrightInteractionAdapter:
    """
    Shared Playwright interaction adapter.

    This can wrap either a Page or Frame because both expose locator().
    """

    def __init__(self, container: Page | FrameLocator):
        self.container = container

    def click(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None:
        self.container.locator(selector).click(timeout=timeout)

    def click_first_child(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None:
        first = self.container.locator(selector).first
        first.wait_for(state="visible", timeout=timeout)
        first.click(timeout=timeout)

    def fill(
        self,
        selector: str,
        text: str,
        timeout: int = 30000,
    ) -> None:
        self.container.locator(selector).fill(str(text), timeout=timeout)

    def text_content(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> str:
        value = self.container.locator(selector).text_content(timeout=timeout)
        return value or ""

    def has_text_content(
        self,
        selector: str,
        text_to_check: str,
        timeout: int = 30000,
    ) -> bool:
        try:
            value = self.container.locator(selector).inner_text(timeout=timeout)
            return value.strip() == text_to_check.strip()

        except PlaywrightTimeoutError:
            return False

    def exists(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> bool:
        try:
            self.container.locator(selector).wait_for(
                state="attached",
                timeout=timeout,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def is_visible(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> bool:
        try:
            self.container.locator(selector).wait_for(
                state="visible",
                timeout=timeout,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_visible(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None:
        self.container.locator(selector).wait_for(
            state="visible",
            timeout=timeout,
        )

    def locator(self, selector: str) -> Locator:
        return self.container.locator(selector)

    def select_item_from_list(
        self,
        selector: str,
        text_to_select: str | int,
        timeout: int = 30000,
    ) -> None:
        text = str(text_to_select).strip()

        items = self.container.locator(selector)
        matching_item = items.filter(has_text=text).first

        matching_item.click(timeout=timeout)

    def select_exact_item_from_list(
        self,
        selector: str,
        text_to_select: str | int,
        timeout: int = 30000,
    ) -> None:
        expected = str(text_to_select).strip()

        items = self.container.locator(selector)
        items.first.wait_for(state="visible", timeout=timeout)

        count = items.count()

        for index in range(count):
            item = items.nth(index)
            actual = item.inner_text(timeout=timeout).strip()

            if actual == expected:
                item.click(timeout=timeout)
                return

        raise ValueError(f"Unable to select item with exact text: {expected}")

    def click_all_items_in_list(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None:
        items = self.container.locator(selector)
        items.first.wait_for(state="visible", timeout=timeout)

        count = items.count()

        for index in range(count):
            items.nth(index).click(timeout=timeout)
