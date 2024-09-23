import json
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
from login_manager import LoginManager
from services.logger import Logger
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

        with open("avaya_rules.json") as f:
            self.config_data = json.load(f)

    def close(self):
        self.driver.close()

    def init_driver(self):
        pass

    def run_webdriver(
        self,
    ):
        try:
            self.driver.get(self.url)
            Logger()
            # ---- LOGIN
            # TODO: put in fn
            login = LoginManager(self.driver, keys["login"], keys["password"])
            login.login()

            # --- Wait for Page Load -> Move to Rules Page
            if self.wELI.wait_for_element(
                10, By.ID, "ctl00_radTabStripSubNavigation", WaitConditions.PRESENCE
            ):
                self.driver.get(self.url + "/ManagerConsole/Delivery/Rules.aspx")

                sleep(3)
                for rule in self.config_data["rules"]:
                    addRuleBtn = self.wELI.wait_for_element(
                    10,
                    By.ID,
                    "ctl00_ActionBarContent_rbAction_Add",
                    WaitConditions.CLICKABLE,
                )
                    if addRuleBtn:
                        self.rule_condition_queues_source = "queues"
                        addRuleBtn.click()
                        # --> Switch to Module Add Rule Popup

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
                        rule_name_input.send_keys(rule["rule_name"])

                        ####TODO PUT in own method / class
                        if "frequency_based" in rule:
                            # Frequency Rule -->
                            freq_time_dropdown = self.wELI.wait_for_element(
                                10,
                                By.XPATH,
                                '//*[contains(@id, "overlayContent_triggerParameters_frequencyComboBox_Arrow")]',
                                WaitConditions.VISIBILITY,
                            )
                            freq_time_dropdown.click()

                            # Set Frequency Rule Time ->>
                            user_time_selection = str(
                                rule["frequency_based"]["time_interval"]
                            )

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
                        if "conditions" in rule and rule["conditions"]:
                            # ---> Select Provider Category

                            for i, condition in enumerate(rule["conditions"]):

                                user_provider_category = condition["provider_category"]

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
                                user_provider_instance = condition["provider_instance"]
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
                                user_provider_condition = condition[
                                    "provider_condition"
                                ]
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
                                condition_details = condition["details"]
                                if condition_details["condition_type"] == "stats":
                                    # equality comparison dropdown
                                    agents_in_after_call_eq_drop = self.wELI.wait_for_element(
                                        10,
                                        By.XPATH,
                                        '//*[contains(@id, "overlayContent_conditionParameters_ddExposedDataOperator_Arrow")]',
                                        WaitConditions.CLICKABLE,
                                    )
                                    agents_in_after_call_eq_drop.click()

                                    # equality comparison operator selection
                                    user_agents_in_after_call_eq = condition_details[
                                        "equality_operator"
                                    ]
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

                                    user_agents_in_after_call_eq_condition = (
                                        condition_details["equality_threshold"]
                                    )

                                    agents_in_after_call_eq_condition.send_keys(
                                        user_agents_in_after_call_eq_condition
                                    )

                                    user_condition_queues = condition_details[
                                        "queues_source"
                                    ]
                                    if user_condition_queues == "users":
                                        # TODO: need getter when made into fn
                                        self.rule_condition_queues_source = "users"
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

                                    if (
                                        i != len(rule["conditions"]) - 1
                                        and len(rule["conditions"]) > 1
                                    ):
                                        add__addit_condition = self.wELI.wait_for_element(
                                            15,
                                            By.XPATH,
                                            '//*[contains(@id, "overlayContent_lblAddCondition")]',
                                            WaitConditions.CLICKABLE,
                                        )
                                        add__addit_condition.click()

                                sleep(3)
                            continue_btn.click()
                        # --->> action page -selection
                        sleep(3)
                        if "actions" in rule and rule["actions"]:
                            for action in rule["actions"]:
                                user_action_category_selection = action[
                                    "provider_category"
                                ]
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
                                sleep(3)

                                user_action_provider_instance = action[
                                    "provider_instance"
                                ]

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
                                user_action_selection = action["provider_condition"]
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

                                if action["details"]["action_type"] == "email":
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
                                    email_subject.send_keys(rule["rule_name"])

                                    if "frequency_based" in rule:
                                        email_message = self.wELI.wait_for_element(
                                            15,
                                            By.XPATH,
                                            '//*[contains(@id, "overlayContent_actionParameters_ctl12")]',
                                            WaitConditions.VISIBILITY,
                                        )
                                    else:
                                        email_message = self.wELI.wait_for_element(
                                            15,
                                            By.XPATH,
                                            '//*[contains(@id, "overlayContent_actionParameters_ctl13")]',
                                            WaitConditions.VISIBILITY,
                                        )

                                    email_message.send_keys(
                                        action["details"]["email_body"]
                                    )
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

                                    if self.rule_condition_queues_source == "users":
                                        input_email_address = self.wELI.wait_for_element(
                                            15,
                                            By.XPATH,
                                            '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
                                            WaitConditions.VISIBILITY,
                                        )

                                    elif self.rule_condition_queues_source == "queues":

                                        input_email_address = self.wELI.wait_for_element(
                                            15,
                                            By.XPATH,
                                            '//*[contains(@id, "overlayContent_actionParameters_ctl61")]',
                                            WaitConditions.VISIBILITY,
                                        )

                                    input_email_address.send_keys(
                                        action["details"]["email_address"]
                                    )

                                if (
                                    i != len(rule["actions"]) - 1
                                    and len(rule["actions"]) > 1
                                ):
                                    add__addit_action = self.wELI.wait_for_element(
                                        15,
                                        By.XPATH,
                                        '//*[contains(@id, "overlayContent_lblAddAction")]',
                                        WaitConditions.CLICKABLE,
                                    )
                                    add__addit_action.click()

                        

                        # Rule category
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
                        sleep(3)
                        submit_btn = self.wELI.wait_for_element(
                            15,
                            By.XPATH,
                            '//*[contains(@id, "overlayButtons_rbSubmit_input")]',
                            WaitConditions.CLICKABLE,
                        )
                        submit_btn.click()

                        try:
                            WebDriverWait(self.driver, 3).until(EC.alert_is_present())

                            alert = self.driver.switch_to.alert
                            if alert.text == f"A Rule with the name {rule["rule_name"]} already exists.":
                                alert.accept()
                                # TODO Ask user to update
                                
                                Logger().insert(
                                "Rule ",
                                "INFO",
                            )   
                                raise ValueError(alert.text)
                            else:
                                raise ValueError(alert.text)
                                Logger().insert(
                                "Session open elsewhere alert was present. Accepted alert to proceed with this session.",
                                "INFO",
                            )
                        except TimeoutException:
                            Logger().insert(f"Rule: {rule["rule_name"]} has been submitted.","INFO")
                        
                        self.driver.switch_to.default_content()
                        success_message = self.wELI.wait_for_element(
                                            15,
                                            By.XPATH,
                                            '//*[contains(@id, "lblMessage")]',
                                            WaitConditions.VISIBILITY,
                                        )
                        if "You have successfully added the Rule" in success_message.text:
                            Logger().insert(f"Rule: {rule["rule_name"]} has been created.","INFO")
            sleep(30)

        except Exception as e:
            print(e)
        finally:
            self.close()


run = WebScrape(keys["url"])
run.run_webdriver()


# except Exception as e:
#                         print(e)
#                     except NoSuchFrameException:
#                         print(
#                             "Iframe not found, make sure you're identifying the iframe correctly."
#                         )