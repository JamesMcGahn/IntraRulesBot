from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..logger.adapters import LogAdapter

from .web_element_interactions import WebElementInteractions
from .enums.wait_conditions import WaitConditions

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
)


class SeleniumBrowserAdapter:

    def __init__(self, driver, logging: LogAdapter):
        self.driver = driver
        self.logging = logging
        self.wELI = WebElementInteractions(self.driver, self.logging)

    def wait_and_click(
        self,
        locator_type: By,
        locator_value: str,
        wait_time: int = 20,
        retries: int = 2,
    ):
        element = self.wELI.wait_for_element(
            wait_time,
            locator_type,
            locator_value,
            WaitConditions.VISIBILITY,
            retries=retries,
            raise_exception=True,
        )
        element.click()

    def select_item_from_list(
        self,
        locator_type: By,
        locator_value: str,
        text_to_select: str | int,
        wait_time: int = 20,
        retries: int = 2,
    ):
        success = self.wELI.select_item_from_list(
            wait_time, locator_type, locator_value, text_to_select, retries=retries
        )
        if not success:
            raise ValueError(f"Unable to select {text_to_select}")

    def wait_and_type(
        self,
        locator_type: By,
        locator_value: str,
        text_to_input: str | int,
        wait_time: int = 20,
        retries: int = 2,
    ):
        element = self.wELI.wait_for_element(
            wait_time,
            locator_type,
            locator_value,
            WaitConditions.VISIBILITY,
            retries=retries,
            raise_exception=True,
        )
        element.clear()
        element.send_keys(text_to_input)

    def click_all_items_in_list(
        self,
        locator_type: By,
        locator_value: str,
        wait_time: int = 20,
        retries: int = 2,
        item_name: str = "",
    ):
        self.wELI.click_all_items_in_list(
            wait_time,
            locator_type,
            locator_value,
            retries=retries,
            item_name=item_name,
        )

    def switch_to_frame(self, locator_type: By, locator_value: str):
        self.wELI.switch_to_frame(20, locator_type, locator_value)

    def wait_for_element(
        self,
        locator_type: By,
        locator_value: str,
        wait_time: int = 20,
        retries: int = 2,
        raise_exception: bool = False,
    ) -> WebElement:
        element = self.wELI.wait_for_element(
            wait_time,
            locator_type,
            locator_value,
            WaitConditions.VISIBILITY,
            raise_exception=raise_exception,
            retries=retries,
        )
        return element

    def switch_to_main_frame(self):
        self.driver.switch_to.default_content()

    def wait_and_accept_alert(self, check_alert_text: str, wait_time: int) -> bool:
        try:
            WebDriverWait(self.driver, wait_time).until(EC.alert_is_present())

            alert = self.driver.switch_to.alert
            if check_alert_text in alert.text:
                alert.accept()

                if alert:
                    return True

        except TimeoutException:
            return False
