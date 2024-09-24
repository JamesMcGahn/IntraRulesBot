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

from actions_worker import ActionsWorker
from conditions_worker import ConditionsWorker
from keys import keys
from login_manager import LoginManager
from services.logger import Logger
from trigger_worker import TriggerWorker
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

                        #Trigger
                        trigger = TriggerWorker(self.driver, rule)
                        trigger.do_work()

                        continue_btn.click()
                        # ------>>> Continue to Condition Page
                        
                        
                        conditions = ConditionsWorker(self.driver, rule)
                        if "conditions" in rule and rule["conditions"]:
                            conditions.do_work()
                            continue_btn.click()
                        # --->> action page -selection
                        sleep(3)
                        actions = ActionsWorker(self.driver,rule)
                        if "actions" in rule and rule["actions"]:
                            actions.rule_condition_queues_source = conditions.rule_condition_queues_source
                            actions.do_work()

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