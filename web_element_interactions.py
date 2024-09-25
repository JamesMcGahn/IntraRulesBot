from enum import Enum
from typing import Optional

from PySide6.QtCore import QObject
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchFrameException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from services.logger import Logger


# TODO: Update with logging
class WaitConditions(Enum):
    PRESENCE = "presence"
    VISIBILITY = "visibility"
    CLICKABLE = "clickable"
    TEXT = "text"
    PRESENCE_OF_ALL = "presence_of_all"
    VISIBILITY_OF_ALL = "visibility_of_all"
    SELECTED = "selected"


class WebElementInteractions(QObject):

    def __init__(self, driver):
        super().__init__()
        self.driver = driver

    def wait_for_element(
        self,
        timeout: int,
        locator_type: By,
        locator_value: str,
        condition: WaitConditions,
        text: Optional[str] = None,
        failure_message: tuple[str, str] = ("WARN", "default"),
    ):
        """
        Args:
            timeout (int): The maximum time (in seconds) the driver should wait for the condition to be met.
            locator_type (By): The type of locator to find the element (e.g., By.ID, By.XPATH).
            locator_value (str): The value of the locator (e.g., the ID or XPATH).
            condition (WaitConditions): The condition to wait for
            text (str, optional): The text to wait for if the condition is 'text'.
            failure_message (Tuple[str, str], optional): A tuple containing a logging warning type and a default message (default is ("WARN", "default"))

        Returns:
            Union[None, WebElement]:
                - Returns None if the operation fails or no element is found.
                - Returns a WebElement if the operation succeeds and an element is found.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            if condition == WaitConditions.PRESENCE:
                element = wait.until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
            elif condition == WaitConditions.VISIBILITY:
                element = wait.until(
                    EC.visibility_of_element_located((locator_type, locator_value))
                )
            elif condition == WaitConditions.CLICKABLE:
                element = wait.until(
                    EC.element_to_be_clickable((locator_type, locator_value))
                )
            elif condition == WaitConditions.TEXT:
                element = wait.until(
                    EC.text_to_be_present_in_element(
                        (locator_type, locator_value), text
                    )
                )
            elif condition == WaitConditions.PRESENCE_OF_ALL:
                elements = wait.until(
                    EC.presence_of_all_elements_located((locator_type, locator_value))
                )
                return elements
            elif condition == WaitConditions.VISIBILITY_OF_ALL:
                elements = wait.until(
                    EC.visibility_of_all_elements_located((locator_type, locator_value))
                )
                return elements
            elif condition == WaitConditions.SELECTED:
                element = wait.until(
                    EC.element_to_be_selected((locator_type, locator_value))
                )

            else:
                raise ValueError(f"Unknown condition: {condition}")
            return element
        except TimeoutException:
            log_level, msg = failure_message
            if msg != "default":
                print()
                # Logger().insert(msg, log_level.upper())

            else:
                print()
                # Logger().insert(
                #     f"Element with {locator_type} = {locator_value} not found within {timeout} seconds.",
                #     "ERROR",
                # )

            return None

    def select_item_from_list(
        self,
        timeout: int,
        locator_type: By,
        locator_value: str,
        text_to_select: str,
        retries: int = 3,
    ):
        """
        Selects an item from a list of elements, retries in case of stale element reference.

        Args:
            timeout: Time in seconds to wait for the list of elements.
            locator_type: Selenium locator type (e.g., By.XPATH).
            locator_value: The locator value (e.g., XPATH or ID for the list of elements).
            text_to_select: The text of the item to be selected.
            retries: Number of retries in case of stale element reference.

        Returns:
            bool: True if the item was successfully clicked, False otherwise.
        """
        for _ in range(retries):
            try:
                # Re-locate the list of elements in each retry to avoid stale element issues
                elements_list = self.wait_for_element(
                    timeout,
                    locator_type,
                    locator_value,
                    WaitConditions.VISIBILITY_OF_ALL,
                )
                if elements_list is None:
                    raise NoSuchElementException
                for item in elements_list:
                    if item.text.strip() == text_to_select:
                        # Logger().insert(f"Selected item: {item.text}", "INFO")

                        item.click()
                        return True  # Successfully clicked, exit
            except StaleElementReferenceException:
                print()
                # Logger().insert("Stale element reference, retrying...", "WARN")
            except NoSuchElementException:
                # Logger().insert(
                #     "No Such element list...check to make sure the locator value is correct",
                #     "ERROR",
                # )
                return False

        # Logger().insert(
        #     f"Failed to select item with text: '{text_to_select}'",
        #     "ERROR",
        # )
        return False

    def click_all_items_in_list(
        self,
        timeout: int,
        locator_type: By,
        locator_value: str,
        retries: int = 3,
        item_name: Optional[str] = None,
    ):
        """
        Selects an item from a list of elements, retries in case of stale element reference.

        Args:
            timeout (int): Time in seconds to wait for the list of elements.
            locator_type (By): Selenium locator type (e.g., By.XPATH).
            locator_value (str): The locator value (e.g., XPATH or ID for the list of elements).
            retries (int): Number of retries in case of stale element reference.
            item_name (str): name of item to specify in print message
        Returns:
            bool: True if the item was successfully clicked, False otherwise.
        """
        for _ in range(retries):
            try:
                # Re-locate the list of elements in each retry to avoid stale element issues
                elements_list = self.wait_for_element(
                    timeout,
                    locator_type,
                    locator_value,
                    WaitConditions.VISIBILITY_OF_ALL,
                )

                for item in elements_list:
                    item.click()
                # Logger().insert(f"All {item_name} items clicked", "INFO")

                return True  # exit inner loop
            except StaleElementReferenceException:
                # Logger().insert("Stale element reference, retrying...", "WARN")
                print()

            return False
        # Logger().insert(f"Failed to click all {item_name} items", "ERROR")
        return False

    def switch_to_frame(self, timeout: int, locator_type: By, locator_value: str):
        """
        Selects an item from a list of elements, retries in case of stale element reference.

        Args:
            timeout (int): Time in seconds to wait for the list of elements.
            locator_type (By): Selenium locator type (e.g., By.XPATH).
            locator_value (str): The locator value (e.g., XPATH or ID for the list of elements).
        Returns:
            bool: True if successfully switched to frame, False otherwise.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((locator_type, locator_value))
            )
            return True
        except NoSuchFrameException:
            # Logger().insert(f"Cannot not find {locator_value} frame.", "ERROR")
            return False
