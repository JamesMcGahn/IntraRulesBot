from typing import Optional

from PySide6.QtCore import QObject, Signal
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchFrameException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .wait_conditions import WaitConditions


class WebElementInteractions(QObject):
    """
    Class responsible for interacting with web elements using Selenium WebDriver.
    Provides methods for waiting for elements, selecting items from lists, and switching frames.

    Attributes:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to interact with the browser.

    Signals:
        send_msg (Signal): Signal used to send logging messages.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
    """

    send_msg = Signal(str, str, bool)

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
        retries: int = 3,
        raise_exception: bool = False,
    ) -> Optional[WebElement]:
        """
        Args:
            timeout (int): The maximum time (in seconds) the driver should wait for the condition to be met.
            locator_type (By): The type of locator to find the element (e.g., By.ID, By.XPATH).
            locator_value (str): The value of the locator (e.g., the ID or XPATH).
            condition (WaitConditions): The condition to wait for.
            text (str, optional): The text to wait for if the condition is 'text'.
            failure_message (Tuple[str, str], optional): A tuple containing a logging warning type and a default message.
            retries (int, optional): Number of retries in case of time out to find element.
        Returns:
            Optional[WebElement]: Returns None if the operation fails or no element is found; returns a WebElement if the operation succeeds.
        """
        for i in range(retries):
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
                        EC.presence_of_all_elements_located(
                            (locator_type, locator_value)
                        )
                    )
                    return elements
                elif condition == WaitConditions.VISIBILITY_OF_ALL:
                    elements = wait.until(
                        EC.visibility_of_all_elements_located(
                            (locator_type, locator_value)
                        )
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
                    self.send_msg.emit(msg, log_level.upper(), True)
                else:
                    self.send_msg.emit(
                        f"Element with {locator_type} = {locator_value} not found within {timeout} seconds.",
                        "ERROR",
                        True,
                    )
                if i < retries - 1:
                    self.send_msg.emit(
                        f"Trying one more time to find Element with {locator_type} = {locator_value}.",
                        "WARN",
                        True,
                    )
        if raise_exception:
            raise NoSuchElementException(
                f"Element with {locator_type} = {locator_value} not found within {timeout} seconds."
            )
        return None

    def select_item_from_list(
        self,
        timeout: int,
        locator_type: By,
        locator_value: str,
        text_to_select: str,
        retries: int = 3,
        raise_exception: bool = False,
    ) -> bool:
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
                        self.send_msg.emit(f"Selected item: {item.text}", "INFO", True)
                        WebDriverWait(self.driver, timeout).until(
                            EC.element_to_be_clickable(item)
                        )
                        item.click()
                        return True  # Successfully clicked, exit
            except StaleElementReferenceException:

                self.send_msg.emit("Stale element reference, retrying...", "WARN", True)
            except NoSuchElementException:
                self.send_msg.emit(
                    "No Such element list...check to make sure the locator value is correct",
                    "ERROR",
                    True,
                )
                return False
            except Exception as e:
                self.send_msg.emit(f"An error occurred: {str(e)}", "ERROR", True)
                if raise_exception:
                    raise Exception(e) from Exception
                return False

        self.send_msg.emit(
            f"Failed to select item with text: '{text_to_select}'",
            "ERROR",
            True,
        )
        if raise_exception:
            raise NoSuchElementException
        return False

    def click_all_items_in_list(
        self,
        timeout: int,
        locator_type: By,
        locator_value: str,
        retries: int = 3,
        item_name: Optional[str] = None,
        raise_exception: bool = False,
    ) -> bool:
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
                    WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable(item)
                    )
                    item.click()
                self.send_msg.emit(f"All {item_name} items clicked", "INFO", True)

                return True  # exit inner loop
            except StaleElementReferenceException:
                self.send_msg.emit("Stale element reference, retrying...", "WARN", True)

            return False
        self.send_msg.emit(f"Failed to click all {item_name} items", "ERROR", True)
        if raise_exception:
            raise Exception
        return False

    def switch_to_frame(
        self,
        timeout: int,
        locator_type: By,
        locator_value: str,
        raise_exception: bool = False,
    ) -> bool:
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
            self.send_msg.emit(f"Cannot not find {locator_value} frame.", "ERROR", True)
            if raise_exception:
                raise NoSuchFrameException from NoSuchFrameException
            return False
