from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from playwright.sync_api import Locator


class InteractionPort(Protocol):

    def click(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None: ...

    def fill(
        self,
        selector: str,
        text: str,
        timeout: int = 30000,
    ) -> None: ...

    def text_content(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> str: ...

    def has_text_content(
        self,
        selector: str,
        text_to_check: str,
        timeout: int = 30000,
    ) -> bool: ...

    def exists(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> bool: ...

    def is_visible(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> bool: ...

    def wait_visible(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None: ...

    def locator(self, selector: str) -> Locator: ...

    def select_item_from_list(
        self,
        selector: str,
        text_to_select: str | int,
        timeout: int = 30000,
    ) -> None: ...

    def select_exact_item_from_list(
        self,
        selector: str,
        text_to_select: str | int,
        timeout: int = 30000,
    ) -> None: ...

    def click_all_items_in_list(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> None: ...
