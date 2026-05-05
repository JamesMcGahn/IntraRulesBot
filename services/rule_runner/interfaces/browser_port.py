from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.remote.webdriver import WebElement


class BrowserPort(Protocol):

    def wait_and_click(
        self,
        locator_type: By,
        locator_value: str,
        wait_time: int = 20,
        retries: int = 3,
    ): ...
    def select_item_from_list(
        self,
        locator_type: By,
        locator_value: str,
        text_to_select: str | int,
        wait_time: int = 20,
        retries: int = 3,
    ): ...

    def wait_and_type(
        self,
        locator_type: By,
        locator_value: str,
        text_to_input: str | int,
        wait_time: int = 20,
        retries: int = 3,
    ): ...

    def click_all_items_in_list(
        self,
        locator_type: By,
        locator_value: str,
        wait_time: int = 20,
        retries: int = 3,
        item_name: str = "",
    ): ...

    def switch_to_frame(self, locator_type: By, locator_value: str): ...

    def wait_for_element(
        self,
        locator_type: By,
        locator_value: str,
        wait_time: int = 20,
        retries: int = 3,
        raise_exception: bool = False,
    ) -> WebElement: ...

    def switch_to_main_frame(self): ...
    def wait_and_accept_alert(self, check_alert_text: str, wait_time: int) -> bool: ...
