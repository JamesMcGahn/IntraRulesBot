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


class ActionsWorker:

    def __init__(self, driver, rule):
        self.driver = driver
        self.rule = rule
        self.wELI = WebElementInteractions(self.driver)
        self._rule_condition_queues_source = "queues"

    @property
    def rule_condition_queues_source(self):
        return self._rule_condition_queues_source

    @rule_condition_queues_source.setter
    def rule_condition_queues_source(self, source):
        self._rule_condition_queues_source = source

    def do_work(self):
        for i, action in enumerate(self.rule["actions"]):
            user_action_category_selection = action["provider_category"]
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

            user_action_provider_instance = action["provider_instance"]

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
                email_subject.send_keys(self.rule["rule_name"])

                if "frequency_based" in self.rule:
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

                email_message.send_keys(action["details"]["email_body"])
                sleep(3)
                continue_btn = self.wELI.wait_for_element(
                    15,
                    By.XPATH,
                    '//*[contains(@id, "overlayButtons_rbContinue_input")]',
                    WaitConditions.CLICKABLE,
                )
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

                if self._rule_condition_queues_source == "users":
                    input_email_address = self.wELI.wait_for_element(
                        15,
                        By.XPATH,
                        '//*[contains(@id, "overlayContent_actionParameters_ctl65")]',
                        WaitConditions.VISIBILITY,
                    )

                elif self._rule_condition_queues_source == "queues":

                    input_email_address = self.wELI.wait_for_element(
                        15,
                        By.XPATH,
                        '//*[contains(@id, "overlayContent_actionParameters_ctl61")]',
                        WaitConditions.VISIBILITY,
                    )

                input_email_address.send_keys(action["details"]["email_address"])

            if i != len(self.rule["actions"]) - 1 and len(self.rule["actions"]) > 1:
                add__addit_action = self.wELI.wait_for_element(
                    15,
                    By.XPATH,
                    '//*[contains(@id, "overlayContent_lblAddAction")]',
                    WaitConditions.CLICKABLE,
                )
                add__addit_action.click()
