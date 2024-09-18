from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchFrameException,
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

    def wait_for_element(self, timeout, locator_type, locator_value, condition):
        """
        Args:
            - timeout: int for how long the driver should wait
            - locator_type:
            - locator_value:
            - condition (str): one of 'presence', 'visibility', or 'clickable'

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
            return element
        except TimeoutException:
            print(
                f"Element with {locator_type} = {locator_value} not found within {timeout} seconds."
            )
            return None

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
                    addRuleBtn.click()
                    # --> Switch to Module Add Rule Popup
                    try:
                        self.driver.switch_to.frame("RadWindowAddEditRule")

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

                            li_elements = WebDriverWait(self.driver, 10).until(
                                EC.visibility_of_all_elements_located(
                                    (
                                        By.XPATH,
                                        '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
                                    )
                                )
                            )
                            # Set Frequency Rule Time ->>
                            time_selection = "5"

                            for item in li_elements:
                                print("Time Frequency item:", item.text)
                                if item.text == time_selection:
                                    print("Selected time frequency of: " + item.text)
                                    item.click()

                            continue_btn.click()
                            # Continue to Condition
                    except NoSuchFrameException:
                        print(
                            "Iframe not found, make sure you're identifying the iframe correctly."
                        )

            sleep(30)

        except Exception as e:
            print(e)


run = WebScrape(keys["url"])
run.run_webdriver()
