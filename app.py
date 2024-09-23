from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchFrameException,
    NoSuchWindowException,
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
from web_element_interactions import WaitConditions, WebElementInteractions


class WebScrape:
    def __init__(self, url):
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(
            options=chrome_options, service=Service(ChromeDriverManager().install())
        )
        self.wELI = WebElementInteractions(self.driver)
        self.not_available = []
        self.source = None
        self.url = url

    def close(self):
        self.driver.close()

    def init_driver(self):
        pass

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

            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())

                alert = self.driver.switch_to.alert
                alert.accept()
                print(
                    "Session open elsewhere alert was present. Accepted alert to proceed with this session."
                )
            except TimeoutException:
                print("No session alert was present.")

            error_login = self.wELI.wait_for_element(
                5,
                By.XPATH,
                '//*[@id="loginErrorContainer"]/span',
                WaitConditions.VISIBILITY,
                failure_message="Login successful.",
            )
            if error_login:
                print("Error during login:", error_login.text)
                return

            # --- Wait for Page Load -> Move to Rules Page
            if self.wELI.wait_for_element(
                10, By.ID, "ctl00_radTabStripSubNavigation", WaitConditions.PRESENCE
            ):
                self.driver.get(self.url + "/ManagerConsole/Delivery/Rules.aspx")
                addRuleBtn = self.wELI.wait_for_element(
                    10,
                    By.ID,
                    "ctl00_ActionBarContent_rbAction_Add",
                    WaitConditions.CLICKABLE,
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
                        if self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayButtonsLeft_cbDontAskLead")]',
                            WaitConditions.CLICKABLE,
                        ):
                            continue_btn = self.wELI.wait_for_element(
                                15,
                                By.XPATH,
                                '//*[contains(@id, "overlayButtons_rbContinue_input")]',
                                WaitConditions.CLICKABLE,
                            )
                            sleep(3)
                            continue_btn.click()

                            # Set Rule Name
                            rule_name_input = self.wELI.wait_for_element(
                                15,
                                By.XPATH,
                                '//*[contains(@id, "overlayRuleProgressArea_tbRuleName")]',
                                WaitConditions.VISIBILITY,
                            )

                            rule_name = "Test Rule"
                            rule_name_input.send_keys(rule_name)

                            # Frequency Rule -->
                            freq_time_dropdown = self.wELI.wait_for_element(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_Arrow")]',
                                WaitConditions.VISIBILITY,
                            )
                            freq_time_dropdown.click()

                            # Set Frequency Rule Time ->>
                            user_time_selection = "5"
                            time_selection = self.wELI.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_DropDown")]/div/ul/li',
                                user_time_selection,
                            )
                            if not time_selection:
                                print(
                                    f"Unable to select time {user_time_selection}. Check that your time selection is one of '1','5','10','15','30','60'"
                                )
                                return
                            sleep(5)
                            continue_btn.click()
                            # ------>>> Continue to Condition Page

                            # ---> Select Provider Category
                            user_provider_category = "ACD"

                            provider_category_select = self.wELI.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_selectCondition_radMenuCategory")]/ul/li',
                                user_provider_category,
                            )
                            if not provider_category_select:
                                print(
                                    f"Unable to select provider category: {user_provider_category}"
                                )
                                return
                            sleep(5)
                            # ---> Select Provider Instance
                            user_provider_instance = "Avaya Test ACD"
                            provider_instance_selection = self.wELI.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_selectCondition_radMenuProviderInstance")]/ul/li',
                                user_provider_instance,
                            )
                            if not provider_instance_selection:
                                print(
                                    f"Unable to select provider {user_provider_instance} "
                                )
                                return
                            # TODO - handle potential value error
                            sleep(5)
                            # ---> Select Provider Condition
                            user_provider_condition = "Agents in Other - By Queue"
                            provider_condition_selection = self.wELI.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_selectCondition_radMenuItem")]/ul/li',
                                user_provider_condition,
                                5,
                            )
                            if not provider_condition_selection:
                                print(
                                    f"Cannot find. Please check that - {user_provider_condition} - is a listed condition for the provider"
                                )
                                return
                            sleep(5)

                            ## Stats Condition

                            # equality comparison dropdown
                            agents_in_after_call_eq_drop = self.wELI.wait_for_element(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_Arrow")]',
                                WaitConditions.CLICKABLE,
                            )
                            agents_in_after_call_eq_drop.click()

                            # equality comparison operator selection
                            user_agents_in_after_call_eq = "Greater Than"
                            agents_in_after_call_eq = self.wELI.select_item_from_list(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_DropDown")]/div/ul/li',
                                user_agents_in_after_call_eq,
                            )
                            if not agents_in_after_call_eq:
                                print(
                                    f"Cant not find {user_agents_in_after_call_eq}. Make sure the comparison operator text is correct"
                                )
                                return

                            # Condition numeric value input to compare
                            agents_in_after_call_eq_condition = self.wELI.wait_for_element(
                                15,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_conditionParameters_tbExposedDataValue")]',
                                WaitConditions.VISIBILITY,
                            )

                            user_agents_in_after_call_eq_condition = 1
                            # TODO raise value error if user input is str
                            agents_in_after_call_eq_condition.send_keys(
                                user_agents_in_after_call_eq_condition
                            )

                            user_condition_queues = "queues"
                            if user_condition_queues == "users":
                                continue_btn.click()
                            elif user_condition_queues == "queues":

                                queues_radio_btn = self.wELI.wait_for_element(
                                    15,
                                    By.XPATH,
                                    '//*[contains(@id, "overlayContent_conditionParameters_ctl16_1")]',
                                    WaitConditions.CLICKABLE,
                                )
                                queues_radio_btn.click()

                                user_queues_dropdown_btn = self.wELI.wait_for_element(
                                    15,
                                    By.XPATH,
                                    '//*[contains(@id, "overlayContent_conditionParameters_ctl22_Arrow")]',
                                    WaitConditions.CLICKABLE,
                                )
                                user_queues_dropdown_btn.click()

                                queues_list = self.wELI.click_all_items_in_list(
                                    10,
                                    By.XPATH,
                                    '//*[contains(@id, "overlayContent_conditionParameters_ctl22_DropDown")]/div/ul/li',
                                    5,
                                    "queues in queues list",
                                )

                                if not queues_list:
                                    return

                                sleep(3)
                                continue_btn.click()
                        # --->> action page -selection
                        sleep(3)
                        user_action_category_selection = "Communications"
                        action_category_dropdown = self.wELI.select_item_from_list(
                            10,
                            By.XPATH,
                            '//*[contains(@id, "overlayContent_selectAction_radMenuCategory")]/ul/li',
                            user_action_category_selection,
                        )
                        if not action_category_dropdown:
                            print(
                                f"Cant not find {action_category_dropdown}. Make sure the provider category for the action text is correct"
                            )
                            return

                        user_action_provider_instance = "Email Provider Instance"

                        sleep(3)
                        action_provider_dropdown = self.wELI.select_item_from_list(
                            10,
                            By.XPATH,
                            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuProviderInstance")]/ul/li',
                            user_action_provider_instance,
                        )
                        if not action_provider_dropdown:
                            print(
                                f"Cant not find {user_action_provider_instance}. Make sure the action provider text is correct"
                            )
                            return

                        sleep(3)
                        user_action_selection = "Send Email"
                        action_selection_dropdown = self.wELI.select_item_from_list(
                            10,
                            By.XPATH,
                            '//*[contains(@id, "ctl00_overlayContent_selectAction_radMenuItem")]/ul/li',
                            user_action_selection,
                        )
                        if not action_selection_dropdown:
                            print(
                                f"Cant not find {user_action_selection}. Make sure the action provider text is correct"
                            )
                            return

                        # Stats based email

                        email_page_settings_btn = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayContent_actionParameters_lblSettings")]',
                            WaitConditions.CLICKABLE,
                        )
                        email_page_settings_btn.click()

                        email_subject = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayContent_actionParameters_ctl05")]',
                            WaitConditions.VISIBILITY,
                        )
                        email_subject.send_keys(rule_name)

                        email_message = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayContent_actionParameters_ctl12")]',
                            WaitConditions.VISIBILITY,
                        )
                        email_message.send_keys("Test Message")
                        sleep(3)
                        continue_btn.click()

                        email_page_users_btn = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayContent_actionParameters_lblUsers")]',
                            WaitConditions.CLICKABLE,
                        )
                        email_page_users_btn.click()

                        select_email_individual = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayContent_actionParameters_rblIntradiemUsersIndividual_Users_1")]',
                            WaitConditions.CLICKABLE,
                        )
                        select_email_individual.click()

                        if user_condition_queues == "users":
                            input_email_address = self.wELI.wait_for_element(
                                15,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
                                WaitConditions.VISIBILITY,
                            )
                            input_email_address.send_keys("Test Message")

                        elif user_condition_queues == "queues":

                            input_email_address = self.wELI.wait_for_element(
                                15,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_actionParameters_ctl61")]',
                                WaitConditions.VISIBILITY,
                            )
                            input_email_address.send_keys("test@example.com")

                        rule_settings_hamburger = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayContent_divAddEditAction")]/div[3]/a',
                            WaitConditions.CLICKABLE,
                        )
                        rule_settings_hamburger.click()
                        sleep(3)

                        self.driver.switch_to.default_content()

                        WebDriverWait(self.driver, 10).until(
                            EC.frame_to_be_available_and_switch_to_it(
                                (By.NAME, "RadWindowAddEditRuleSettings")
                            )
                        )

                        rule_category_dropdown_arrow = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "ddRuleCategory_Arrow")]',
                            WaitConditions.CLICKABLE,
                        )
                        rule_category_dropdown_arrow.click()

                        self.wELI.select_item_from_list(
                            10,
                            By.XPATH,
                            '//*[contains(@id, "ddRuleCategory_DropDown")]/div/ul/li',
                            "Other - Admin",
                        )
                        sleep(3)
                        self.driver.switch_to.default_content()
                        WebDriverWait(self.driver, 10).until(
                            EC.frame_to_be_available_and_switch_to_it(
                                (By.NAME, "RadWindowAddEditRule")
                            )
                        )

                        continue_btn.click()
                        try:
                            WebDriverWait(self.driver, 5).until(EC.alert_is_present())

                            alert = self.driver.switch_to.alert
                            alert.accept()
                            print("There is something wrong with your email.")
                            # continue when in actual Loop
                            # print("Skipping Rule - rule name")
                        except TimeoutException:
                            print("No alert was present after login.")

                        # to submit
                        # ctl00_overlayButtons_rbSubmit_input

                    except Exception as e:
                        print(e)
                    except NoSuchFrameException:
                        print(
                            "Iframe not found, make sure you're identifying the iframe correctly."
                        )

            sleep(30)

        except Exception as e:
            print(e)
        finally:
            self.close()


run = WebScrape(keys["url"])
run.run_webdriver()
