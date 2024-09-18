from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchFrameException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from keys import keys


class WebScrape:
    def __init__(self, url):
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(
            options=chrome_options, service=Service(ChromeDriverManager().install())
        )
        self.not_available = []
        self.source = None
        self.url = url

    def close(self):
        self.driver.close()

    def init_driver(self):
        pass

    def wait_for_element(
        self, timeout, locator_type, locator_value, condition, text=None
    ):
        """
        Args:
            - timeout: int for how long the driver should wait
            - locator_type (By): The type of locator to find the element (e.g., By.ID, By.XPATH).
            - locator_value (str): The locator value (e.g., the ID or XPATH).
            - condition (str): one of 'presence', 'visibility', 'clickable', 'text', 'presence_of_all', 'visibility_of_all', 'selected'
            - text (str, optional): The text to wait for if the condition is 'text'.

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
                # Find and click the item that matches the provided text
                for item in elements_list:
                    if item.text.strip() == text_to_select:
                        print(f"Selected item: {item.text}")
                        item.click()
                        return True  # Successfully clicked, exit the function
            except StaleElementReferenceException:
                print("Stale element reference, retrying...")

        print(f"Failed to select item with text: '{text_to_select}'")
        return False

    def run_webdriver(
        self,
    ):
        try:
            self.driver.get(self.url)

            # ---- LOGIN
            # TODO: put in fn
            login_name_field = self.driver.find_element(By.ID, "inputUserName")
            login_name_field.send_keys(keys["login"])

            login_pw_field = self.driver.find_element(By.ID, "inputPassword")
            login_pw_field.send_keys(keys["password"])

            login_btn = self.driver.find_element(By.ID, "btnLogin")
            login_btn.click()

            # ---- LOGIN - Session Alert
            try:
                WebDriverWait(self.driver, 10).until(EC.alert_is_present())

                alert = self.driver.switch_to.alert
                alert.accept()
                print("Alert was present and accepted.")
            except TimeoutException:
                print("No alert was present after login.")

            # --- Wait for Page Load -> Move to Rules Page
            if self.wait_for_element(
                10, By.ID, "ctl00_radTabStripSubNavigation", "presence"
            ):
                self.driver.get(self.url + "/ManagerConsole/Delivery/Rules.aspx")
                addRuleBtn = self.wait_for_element(
                    10, By.ID, "ctl00_ActionBarContent_rbAction_Add", "clickable"
                )
                if addRuleBtn:
                    sleep(3)
                    addRuleBtn.click()
                    # --> Switch to Module Add Rule Popup
                    try:

                        WebDriverWait(self.driver, 10).until(
                            EC.frame_to_be_available_and_switch_to_it(
                                (By.NAME, "RadWindowAddEditRule")
                            )
                        )
                        # --> If Tuturial Page Info Present -> Skip Page
                        if self.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayButtonsLeft_cbDontAskLead")]',
                            "clickable",
                        ):
                            continue_btn = self.wait_for_element(
                                15,
                                By.XPATH,
                                '//*[contains(@id, "overlayButtons_rbContinue_input")]',
                                "clickable",
                            )
                            sleep(3)
                            continue_btn.click()

                            # Set Rule Name
                            rule_name_input = self.wait_for_element(
                                15,
                                By.XPATH,
                                '//*[contains(@id, "overlayRuleProgressArea_tbRuleName")]',
                                "visibility",
                            )

                            rule_name = "Test Rule"
                            rule_name_input.send_keys(rule_name)

                            # Frequency Rule -->
                            freq_time_dropdown = self.wait_for_element(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_Arrow")]',
                                "visibility",
                            )
                            freq_time_dropdown.click()

                            # Set Frequency Rule Time ->>
                            user_time_selection = "5"
                            time_selection = self.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
                                user_time_selection,
                            )
                            if not time_selection:
                                print(
                                    f"Unable to select time {user_time_selection}. Check that your time selection is one of '1','5','10','15','30','60'"
                                )
                            sleep(5)
                            continue_btn.click()
                            # ------>>> Continue to Condition Page

                            # ---> Select Provider Category
                            user_provider_category = "ACD"

                            provider_category_select = self.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_selectCondition_radMenuCategory")]/ul/li',
                                user_provider_category,
                            )
                            if not provider_category_select:
                                return
                                print(
                                    f"Unable to select provider category: {user_provider_category}"
                                )

                            # ---> Select Provider Instance
                            user_provider_instance = "Avaya Test ACD"
                            provider_instance_selection = self.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
                                user_provider_instance,
                            )
                            if not provider_instance_selection:
                                return
                                print(
                                    f"Unable to select provider {user_provider_instance} "
                                )
                            # TODO - handle potential value error

                            # ---> Select Provider Condition
                            user_provider_condition = "Agents in Other - By Queue"
                            provider_condition_selection = self.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_selectCondition_radMenuItem")]/ul/li',
                                user_provider_condition,
                            )
                            if not provider_condition_selection:
                                return
                                print(
                                    f"Cannot find. Please check that - {provider_condition_selection} - is a listed condition for the provider"
                                )

                            sleep(5)

                            continue_btn.click()

                            # --->> ACTION Page

                    except NoSuchFrameException:
                        print(
                            "Iframe not found, make sure you're identifying the iframe correctly."
                        )

            sleep(30)

        except Exception as e:
            print(e)


run = WebScrape(keys["url"])
run.run_webdriver()
