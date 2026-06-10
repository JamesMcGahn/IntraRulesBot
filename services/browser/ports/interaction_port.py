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

    def click_first_child(
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

    def find_by_has_text(
        self,
        base_selector: str,
        has_selector: str,
        text: str,
        strict_exact: bool = False,
    ) -> Locator: ...

    def find_child_by_has_text(
        self,
        parent: Locator,
        base_selector: str,
        has_selector: str,
        text: str,
        strict_exact: bool = False,
    ) -> Locator: ...

    def click_inside_parent(
        self,
        parent: Locator,
        selector: str,
        timeout: int = 30000,
        no_wait_after: bool = False,
    ) -> None: ...

    def wait_for_locator_visible(
        self,
        locator: Locator,
        timeout: int = 30000,
    ) -> None: ...

    def frame_locator(self, selector: str) -> InteractionPort: ...

    def wait_for_loading_cycle(
        self,
        selector: str,
        appear_timeout: int = 1000,
        disappear_timeout: int = 30000,
    ) -> None: ...

    def find_by_has_selector(
        self, base_selector: str, has_selector: str
    ) -> Locator: ...

    def get_attribute_inside_parent(
        self, parent: Locator, selector: str, attribute: str, timeout: int = 30000
    ) -> str: ...
