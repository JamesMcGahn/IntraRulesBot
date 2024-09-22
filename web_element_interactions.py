from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# TODO: use Enums?
class WebElementInteractions:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(
        self,
        timeout: int,
        locator_type,
        locator_value,
        condition,
        text=None,
        failure_message="default",
    ):
        """
        Args:
            - timeout : int for how long the driver should wait
            - locator_type (By): The type of locator to find the element (e.g., By.ID, By.XPATH).
            - locator_value (str): The locator value (e.g., the ID or XPATH).
            - condition (str): one of 'presence', 'visibility', 'clickable', 'text', 'presence_of_all', 'visibility_of_all', 'selected'
            - text (str, optional): The text to wait for if the condition is 'text'.
            - failure_message (str,optional): Override the default failure message with your custom message
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            if condition == "presence":
                element = wait.until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
            elif condition == "visibility":
                element = wait.until(
                    EC.visibility_of_element_located((locator_type, locator_value))
                )
            elif condition == "clickable":
                element = wait.until(
                    EC.element_to_be_clickable((locator_type, locator_value))
                )
            elif condition == "text":
                element = wait.until(
                    EC.text_to_be_present_in_element(
                        (locator_type, locator_value), text
                    )
                )
            elif condition == "presence_of_all":
                elements = wait.until(
                    EC.presence_of_all_elements_located((locator_type, locator_value))
                )
                return elements
            elif condition == "visibility_of_all":
                elements = wait.until(
                    EC.visibility_of_all_elements_located((locator_type, locator_value))
                )
                return elements
            elif condition == "selected":
                element = wait.until(
                    EC.element_to_be_selected((locator_type, locator_value))
                )

            else:
                raise ValueError(f"Unknown condition: {condition}")
            return element
        except TimeoutException:
            if failure_message != "default":
                print(failure_message)
            else:
                print(
                    f"Element with {locator_type} = {locator_value} not found within {timeout} seconds."
                )

            return None

    def select_item_from_list(
        self, timeout, locator_type, locator_value, text_to_select, retries=3
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
                    "visibility_of_all",
                )
                if elements_list is None:
                    raise NoSuchElementException
                for item in elements_list:
                    if item.text.strip() == text_to_select:
                        print(f"Selected item: {item.text}")
                        item.click()
                        return True  # Successfully clicked, exit
            except StaleElementReferenceException:
                print("Stale element reference, retrying...")
            except NoSuchElementException:
                print(
                    "No Such element list...check to make sure the locator value is correct"
                )
                return False

        print(f"Failed to select item with text: '{text_to_select}'")
        return False

    def click_all_items_in_list(
        self, timeout, locator_type, locator_value, retries=3, item_name=None
    ):
        """
        Selects an item from a list of elements, retries in case of stale element reference.

        Args:
            timeout (int): Time in seconds to wait for the list of elements.
            locator_type: Selenium locator type (e.g., By.XPATH).
            locator_value : The locator value (e.g., XPATH or ID for the list of elements).
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
                    "visibility_of_all",
                )

                for item in elements_list:
                    item.click()
                print(f"All {item_name} items clicked")
                return True  # exit inner loop
            except StaleElementReferenceException:
                print("Stale element reference, retrying...")

            return False
        print(f"Failed to click all {item_name} items")
        return False
