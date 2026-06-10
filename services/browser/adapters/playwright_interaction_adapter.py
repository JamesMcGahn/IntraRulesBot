from __future__ import annotations

import re

from playwright.sync_api import (
    FrameLocator,
    Locator,
    Page,
)
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


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

    def find_by_has_text(
        self,
        base_selector: str,
        has_selector: str,
        text: str,
        strict_exact: bool = False,
    ) -> Locator:
        has_text = re.compile(rf"^{re.escape(text)}$") if strict_exact else text
        return self.container.locator(base_selector).filter(
            has=self.container.locator(has_selector, has_text=has_text)
        )

    def find_child_by_has_text(
        self,
        parent: Locator,
        base_selector: str,
        has_selector: str,
        text: str,
        strict_exact: bool = False,
    ) -> Locator:
        has_text = re.compile(rf"^{re.escape(text)}$") if strict_exact else text
        return parent.locator(base_selector).filter(
            has=self.container.locator(has_selector, has_text=has_text)
        )

    def click_inside_parent(
        self,
        parent: Locator,
        selector: str,
        timeout: int = 30000,
        no_wait_after: bool = False,
    ) -> None:
        parent.locator(selector).click(timeout=timeout, no_wait_after=no_wait_after)

    def wait_for_locator_visible(
        self,
        locator: Locator,
        timeout: int = 30000,
    ) -> None:
        locator.wait_for(state="visible", timeout=timeout)

    def frame_locator(self, selector: str) -> PlaywrightInteractionAdapter:
        frame = self.container.frame_locator(selector)
        if frame is None:
            raise ValueError(f"Frame not found: {selector}")

        return PlaywrightInteractionAdapter(frame)

    def wait_for_loading_cycle(
        self,
        selector: str,
        appear_timeout: int = 1000,
        disappear_timeout: int = 30000,
    ) -> None:

        loader = self.container.locator(selector)
        try:
            loader.wait_for(state="visible", timeout=appear_timeout)
        except PlaywrightTimeoutError:
            print("loader wasnt there")
            return
        print("loader was there")
        loader.wait_for(state="hidden", timeout=disappear_timeout)

    def find_by_has_selector(self, base_selector: str, has_selector: str) -> Locator:

        return self.container.locator(base_selector).filter(
            has=self.container.locator(has_selector)
        )

    def get_attribute_inside_parent(
        self, parent: Locator, selector: str, attribute: str, timeout: int = 30000
    ) -> str:
        value = parent.locator(selector).get_attribute(attribute, timeout=timeout)
        return value or ""
